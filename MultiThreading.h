#ifndef MULTITHREADING_H
#define MULTITHREADING_H

#include <thread>
#include <windows.h>

/// In order for a function to be able to be multi-threaded, its header should look like:
/// DWORD WINAPI FunctionName(LPVOID void_pointer)
/// the return value is 0 for success or anything else for a failure (like main), and doesn't get recorded by this library
/// the argument is a single void pointer (LPVOID is a typedef for *void)

using namespace std;

struct ThreadStruct
{
    uint64_t len;
    void **dat;
    LPTHREAD_START_ROUTINE func;
    uint64_t id;
};

DWORD WINAPI autoSplitHelper(LPVOID threadStruct);

class MultiThreading
{
	public:
		MultiThreading(LPTHREAD_START_ROUTINE func, void ** data, uint64_t len);
		uint64_t getThreadCount();
		void setThreadCount(uint64_t newThreadCount);
		void reduceThreadCount(uint64_t reduceAmmount);
		void increaseThreadCount(uint64_t increaseAmmount);
		void reserveThreads(uint64_t reduceAmmount);
		~MultiThreading();
		void autoStart();
		void autoSplit();

	protected:
	    uint64_t threadCount;
		LPTHREAD_START_ROUTINE f;
		void **dat;
		uint64_t len;

	private:
};

#endif // MULTITHREADING_H
