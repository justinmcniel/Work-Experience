#include "MultiThreading.h"

#include <iostream>
#include <thread>
#include <windows.h>

using namespace std;

MultiThreading::MultiThreading(LPTHREAD_START_ROUTINE func, void ** data, uint64_t len)
{

    #ifdef thread
        this->threadCount = (uint64_t)thread::hardware_concurrency();
    #else
        SYSTEM_INFO sysinfo;
        GetSystemInfo(&sysinfo);
        this->threadCount = (uint64_t)sysinfo.dwNumberOfProcessors;
    #endif // thread
    this->f = func;
    this->dat = data;
    this->len = len;
}

uint64_t MultiThreading::getThreadCount()
{
    return this->threadCount;
}

void MultiThreading::setThreadCount(uint64_t newThreadCount)
{
    this->threadCount = newThreadCount;
    return;
}

void MultiThreading::reduceThreadCount(uint64_t reduceAmmount)
{
    this->threadCount -= reduceAmmount;
    return;
}

void MultiThreading::increaseThreadCount(uint64_t increaseAmmount)
{
    this->threadCount += increaseAmmount;
    return;
}

void MultiThreading::reserveThreads(uint64_t reduceAmmount)
{
    this->threadCount -= reduceAmmount;
    return;
}

void MultiThreading::autoSplit()
{
    uint64_t lens[this->threadCount];

    uint16_t breakPoint = (this->len) % this->threadCount;
    lens[0] = (uint64_t)(this->len / this->threadCount);

    uint64_t highestLen = 0;

    for(uint64_t i = 1; i < this->threadCount; i++)
    {
        lens[i] = lens[0];
        if(i <= breakPoint)  // thread 0 has the basic number, then threads 1-n have +1 data block for n extra data blocks
        {
            lens[i]++;
        }
        if(lens[i] > highestLen)
        {
            highestLen = lens[i];
        }
    }

    void **dats[this->threadCount];

    for(uint64_t i = 0; i < this->threadCount; i++)
    {
        dats[i] = (void**)malloc(sizeof(void*)*highestLen);
    }

    uint64_t datPtrs[this->threadCount];

    for(uint64_t i = 0; i < this->threadCount; i++)
    {
        datPtrs[i] = 0;
    }

    uint64_t datPtr = 0;

    while(datPtr < this->len)
    {
        for(uint64_t i = 0; i < this->threadCount; i++)
        {
            if(datPtrs[i] < lens[i])
            {
                dats[i][datPtrs[i]] = this->dat[datPtr];
                datPtrs[i]++;
                datPtr++;
                if(datPtr >= this->len)
                {
                    for(uint64_t i = 0; i < this->threadCount; i++)
                    {
                        lens[i] = datPtrs[i];
                    }
                    break;
                }
            }
        }
    }

    for(uint64_t i = 0; i < this->threadCount; i++)
    {
        if(datPtrs[i] != lens[i])
        {
            cout << "Error: Thread " << i << " still has " << lens[i]-datPtrs[i] << " left." << endl;
        }
    }

    DWORD threadIdPtr[this->threadCount];
	HANDLE hThread[this->threadCount];

    ThreadStruct thStructs[this->threadCount];

	for(uint64_t i = 0; i < this->threadCount; i++)
    {
        thStructs[i].dat = dats[i];
        thStructs[i].len = lens[i];
        thStructs[i].func = this->f;
        thStructs[i].id = i;

        hThread[i] = CreateThread(NULL, 0, autoSplitHelper, (void*)(&(thStructs[i])), 0, &threadIdPtr[i]);
    }

	WaitForMultipleObjects(this->threadCount, hThread, true, INFINITE);

	for(uint64_t i = 0; i < this->threadCount; i++)
    {
		CloseHandle(hThread[i]);

		//So that the compiler doesn't have the main thread delete this array off of the stack before the other threads use its contents
		threadIdPtr[i] = 0;
		thStructs[i].dat = nullptr;
		thStructs[i].len = 0;
		thStructs[i].func = nullptr;
		thStructs[i].id = 0;

		free(dats[i]);
		dats[i] = nullptr;
    }
}

DWORD WINAPI autoSplitHelper(LPVOID threadStruct)
{
    ThreadStruct *thStruct = (ThreadStruct*)threadStruct;

    for(uint64_t i = 0; i < thStruct->len; i++)
    {
        (thStruct->func)(thStruct->dat[i]);
    }
    return 0;
}

void MultiThreading::autoStart()
{
    {
	//Was Experimenting with this, IDK if it works
	/*
	LPSECURITY_ATTRIBUTES secAtt;
	secAtt->bInheritHandle = false;

	SECURITY_DESCRIPTOR secDesc;
	while(!SetSecurityDescriptorDacl(&secDesc, false, nullptr, NULL))
	{
		cout << "Trying to set SecurityDescriptorDacl." << endl;
	}
	while(!SetSecurityDescriptorGroup(&secDesc, ))

	secAtt->lpSecurityDescriptor = &(secDesc);
	secAtt->nLength = sizeof(*secAtt);
	*/

    /*
	DWORD threadIdPtr[this->threadCount];
	HANDLE hThread[this->threadCount];
	int currentThreads = 0;
	bool open[this->threadCount];
	for(int i = 0; i < this->threadCount; i++)
	{
		open[i]=true;
	}
	uint64_t dataPtr=0;

	while(dataPtr < this->len)
	{
		for(int i = 0; i < this->threadCount; i++)
		{
			if(open[i])
			{
				//hThread[i] = CreateThread(secAtt, 0, this->f, this->dat[dataPtr], 0, &threadIdPtr[i]);
				hThread[i] = CreateThread(NULL, 0, this->f, this->dat[dataPtr], 0, &threadIdPtr[i]);
				open[i] = false;
				dataPtr++;
				currentThreads++;
			}
		}
		DWORD finished=WaitForMultipleObjects(currentThreads, hThread, false, INFINITE);
		open[finished-WAIT_OBJECT_0] = true;
		currentThreads--;
	}
	WaitForMultipleObjects(currentThreads, hThread, true, INFINITE);
	/*/
    }

	DWORD threadIdPtr[this->threadCount];
	HANDLE hThread[this->threadCount];
	uint64_t dataPtr = 0;
	for(uint64_t i = 0; i < this->threadCount; i++)
    {
        hThread[i] = CreateThread(NULL, 0, this->f, this->dat[dataPtr], 0, &threadIdPtr[i]);
        dataPtr++;
    }
    while(dataPtr < this->len)
    {
		DWORD finished=WaitForMultipleObjects(this->threadCount, hThread, false, INFINITE);
		CloseHandle(hThread[finished-WAIT_OBJECT_0]);
		hThread[finished-WAIT_OBJECT_0]=CreateThread(NULL, 0, this->f, this->dat[dataPtr], 0, &threadIdPtr[finished-WAIT_OBJECT_0]);
		dataPtr++;
	}
	WaitForMultipleObjects(this->threadCount, hThread, true, INFINITE);
	//*/

	for(uint64_t i = 0; i < this->threadCount; i++)
    {
		CloseHandle(hThread[i]);
    }
}

MultiThreading::~MultiThreading()
{
    this->f = nullptr;
	this->dat = nullptr;
	this->len = 0;
}
