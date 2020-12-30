#include <iostream>
#include <math.h>
#include <quadmath.h>
#include <stdio.h>
#include <fcntl.h>
#include <io.h>
#include <string>
#include <fstream>

#include "MultiThreading.h"

using namespace std;
//*
typedef long double floatingPoint;
/*/
typedef __float128 floatingPoint;
#define round(x) roundq(x)
#define pow(x, y) powq(x, y)
#define atan2(x, y) atan2q(x, y)
#define cos(x) cosq(x)
#define sin(x) sinq(x)
#define sqrt(x) sqrtq(x)
#define log(x) logq(x)
#define floor(x) floorq(x)
#define abs(x) fabsq(x)
#define isnan(x) isnanq(x)
#define log10(x) log10q(x)
#define ceil(x) ceilq(x)
//*/

typedef floatingPoint storageType;

#define AutoSplit 0
#define AutoStart 1

uint8_t multiThreadingMode = AutoSplit;

storageType max_iteration = 1000;
uint8_t storageSizeInBytes;

bool piping = true;

floatingPoint maxHue = 0.0;

uint16_t reservedThreads = 0;
uint16_t useThreads = 0;

floatingPoint xSpacing = 0.01;
floatingPoint ySpacing = 0.01;

int pixelWidth = 0;
int pixelHeight = 0;

bool testing = true;

uint8_t xRoundDigits;
floatingPoint xSpacingRoundHelper0;
floatingPoint xSpacingRoundHelper1;
floatingPoint xSpacingRoundHelper2;
floatingPoint xSpacingRoundHelper3;
floatingPoint xSpacingRoundHelper4;

floatingPoint xSpacingRound(floatingPoint x)
{
    return xSpacingRoundHelper3*round(x*xSpacingRoundHelper4);
}

uint8_t yRoundDigits;
floatingPoint ySpacingRoundHelper0;
floatingPoint ySpacingRoundHelper1;
floatingPoint ySpacingRoundHelper2;
floatingPoint ySpacingRoundHelper3;
floatingPoint ySpacingRoundHelper4;

floatingPoint ySpacingRound(floatingPoint y)
{
    return ySpacingRoundHelper3*round(y*ySpacingRoundHelper4);
}

floatingPoint xStart = -2.0;
floatingPoint yStart = -1.0;
floatingPoint xEnd = 1.0;
floatingPoint yEnd = 1.0;

char deliminator = '\n';

char *outFile = nullptr;

floatingPoint jx = 0.0;
floatingPoint jy = 0.0;
floatingPoint jp = 2.0;

storageType juliaGetItters(floatingPoint px, floatingPoint py)
{

    uint64_t iteration = 0;

    floatingPoint tmp0, tmp1, tmp2, halfJP;

    halfJP = jp/2.0;

    tmp0 = px*px+py*py;

    while(tmp0 < 4 && iteration < max_iteration)
    {
        tmp1 = pow(tmp0,halfJP);
        tmp2 = jp*atan2(py,px);

        px=tmp1*cos(tmp2)+jx;
        py=tmp1*sin(tmp2)+jy;

        tmp0 = px*px+py*py;

        iteration ++;
    }

    tmp1 = pow(tmp0,halfJP);
    tmp2 = jp*atan2(py,px);

    px=tmp1*cos(tmp2)+jx;
    py=tmp1*sin(tmp2)+jy;

    tmp1 = pow(px*px+py*py,halfJP);
    tmp2 = jp*atan2(py,px);

    px=tmp1*cos(tmp2)+jx;
    py=tmp1*sin(tmp2)+jy;

    return (floatingPoint)(iteration + 3) - log(log(sqrt(px*px+py*py)))/log(jp);
}

typedef struct Pixel
{
    floatingPoint f1;
    floatingPoint f2;

    uint8_t r;
    uint8_t g;
    uint8_t b;

    uint64_t histogram_total;
    uint64_t *histogram;
} Pixel;

DWORD WINAPI renderPixel(LPVOID inPtr)
{
    Pixel *pix = (Pixel*)inPtr;

    pix->f1 = juliaGetItters(pix->f1, pix->f2);

    return 0;
}

void printIter(Pixel *pix)
{
    cout << (char)pix->r << (char)pix->g << (char)pix->b;
}

void printIter(uint32_t n)
{
    unsigned char* res = (unsigned char*)malloc(storageSizeInBytes);

    for(int i = 0; i < storageSizeInBytes; i++)
    {
        res[i] = n%0x100;
        n = n>>8;
    }

    for(int i = storageSizeInBytes-1; i >= 0; i--)
    {
        cout << res[i];
    }

    free(res);
    res = nullptr;
}

floatingPoint linear_interpolate(floatingPoint v0, floatingPoint v1, floatingPoint t)
{
    return (1.0 - t) * v0 + t * v1;
}

floatingPoint getHue(storageType x, uint64_t *histogram, uint64_t histogram_total)
{
    floatingPoint hue0 = 0.0;
    for(int i = 0; i < (int)floor(x); i++)
    {
        hue0 += (floatingPoint)histogram[i];
    }
    hue0 /= histogram_total;
    floatingPoint hue1 = hue0;
    hue1 += ((floatingPoint)histogram[(int)floor(x)])/histogram_total;

    floatingPoint time = x - floor(x);

    floatingPoint hue = linear_interpolate(hue0, hue1, time);
    return hue;
}

struct Color
{
    floatingPoint v1;
    floatingPoint v2;
    floatingPoint v3;
};

floatingPoint mod2(floatingPoint x)
{
    x /= 2.0;
    floatingPoint tmp = x - floor(x);
    if(tmp != 0.0)
    {
        x = tmp;
    }
    x *= 2.0;
    return x;
}

floatingPoint mod1(floatingPoint x)
{
    floatingPoint tmp = x - floor(x);
    if(tmp != 0.0)
    {
        x = tmp;
    }
    return x;
}

Color hsv_to_rgb(Color hsv)
{
    Color rgb;

    floatingPoint h = mod1(hsv.v1) * 360;
    floatingPoint s = mod1(hsv.v2);
    floatingPoint v = mod1(hsv.v3);

    floatingPoint C = v*s;
    floatingPoint X = C*(1 - abs(mod2(h/60.0) - 1));
    floatingPoint m = v - C;

    floatingPoint Rp = 0.0;
    floatingPoint Gp = 0.0;
    floatingPoint Bp = 0.0;

    if(h < 60)
    {
        Rp = C;
        Gp = X;
        Bp = 0.0;
    }
    else if(h < 120)
    {
        Rp = X;
        Gp = C;
        Bp = 0.0;
    }
    else if(h < 180)
    {
        Rp = 0.0;
        Gp = C;
        Bp = X;
    }
    else if(h < 240)
    {
        Rp = 0.0;
        Gp = X;
        Bp = C;
    }
    else if(h < 300)
    {
        Rp = X;
        Gp = 0.0;
        Bp = C;
    }
    else
    {
        Rp = C;
        Gp = 0.0;
        Bp = X;
    }

    rgb.v1 = Rp + m;
    rgb.v2 = Gp + m;
    rgb.v3 = Bp + m;
    return rgb;
}

floatingPoint minimum(floatingPoint a, floatingPoint b)
{
    if(a<b)
    {
        return a;
    }
    return b;
}

floatingPoint sigmoid(floatingPoint a)
{
    return 1/(1+pow(2.7182818284590452353602874,-a));
}

DWORD WINAPI huePalette(LPVOID pixP)
{
    Pixel *pix = (Pixel*)pixP;

    if(isnan(pix->f1))
    {
        pix->r = 0;
        pix->g = 0;
        pix->b = 0;
        return 0;
    }
    floatingPoint hue = getHue(pix->f1, pix->histogram, pix->histogram_total);
    floatingPoint h = hue/3*2 + 0.72 +1/9;
    floatingPoint s = sigmoid((hue-.5)*8+3);
    floatingPoint v = 0.8;

    Color hsv;
    hsv.v1 = h;
    hsv.v2 = s;
    hsv.v3 = v;

    Color rgb = hsv_to_rgb(hsv);

    (*pix).r = rgb.v1*255;
    (*pix).g = rgb.v2*255;
    (*pix).b = rgb.v3*255;

    return 0;
}

/// TODO: Test arguments for julia center and power
int main(int argc, char **argv)
{
    bool changeXStart = false;
    bool changeXEnd = false;
    bool changeYStart = false;
    bool changeYEnd = false;

    for(int i = 1; i < argc; i++)
    {
        char *lowerArg = strlwr(argv[i]);
        if(argv[i][0] != '-')
        {
            return 1;
        }

        if(strcmp(lowerArg, "-p") == 0 || strcmp(lowerArg, "--piping") == 0 || strcmp(lowerArg, "--pipe") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 2;
            }
            lowerArg = strlwr(argv[i]);

            if((lowerArg[0] == 'o' && lowerArg[1] == 'n') || lowerArg[0] == 't' || lowerArg[0] == 'y' || lowerArg[0] == '1')
            {
                piping = true;
            }
            else if((lowerArg[0] == 'o' && lowerArg[1] == 'f') || lowerArg[0] == 'f' || lowerArg[0] == 'n' || lowerArg[0] == '0')
            {
                piping = false;
            }
            else
            {
                return 3;
            }
        }
        else if(strcmp(lowerArg, "-xs") == 0 || strcmp(lowerArg, "--xstep") == 0 || strcmp(lowerArg, "--xstepping") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 4;
            }

            xSpacing = atof(argv[i]);

            if(xSpacing == 0.0)
            {
                return 5;
            }
        }
        else if(strcmp(lowerArg, "-ys") == 0 || strcmp(lowerArg, "--ystep") == 0 || strcmp(lowerArg, "--ystepping") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 6;
            }

            ySpacing = atof(argv[i]);

            if(ySpacing == 0.0)
            {
                return 7;
            }
        }
        else if(strcmp(lowerArg, "-xb") == 0 || strcmp(lowerArg, "--xbound") == 0 || strcmp(lowerArg, "--xbounds") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 8;
            }
            lowerArg = strlwr(argv[i]);

            if(lowerArg[0] == '(')
            {
                changeXStart = true;
            }
            else if(lowerArg[0] == '[')
            {
                changeXStart = false;
            }
            else
            {
                return 9;
            }

            if(lowerArg[strlen(argv[i])-2] == ')')
            {
                changeXEnd = true;
            }
            else if(lowerArg[strlen(argv[i])-2] == ']')
            {
                changeXEnd = false;
            }
            else
            {
                return 0xA;
            }

            char *num1 = (&(lowerArg[1]));
            char *num2 = (&(strchr(lowerArg,',')[1]));

            lowerArg[strlen(argv[i])-2] = '\0';
            strchr(lowerArg,',')[0] = '\0';

            xStart = atof(num1);
            xEnd = atof(num2);
        }
        else if(strcmp(lowerArg, "-yb") == 0 || strcmp(lowerArg, "--ybound") == 0 || strcmp(lowerArg, "--ybounds") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0xB;
            }
            lowerArg = strlwr(argv[i]);

            if(lowerArg[0] == '(')
            {
                changeYStart = true;
            }
            else if(lowerArg[0] == '[')
            {
                changeYStart = false;
            }
            else
            {
                return 0xC;
            }

            if(lowerArg[strlen(argv[i])-2] == ')')
            {
                changeYEnd = true;
            }
            else if(lowerArg[strlen(argv[i])-2] == ']')
            {
                changeYEnd = false;
            }
            else
            {
                return 0xD;
            }

            char *num1 = (&(lowerArg[1]));
            char *num2 = (&(strchr(lowerArg,',')[1]));

            lowerArg[strlen(argv[i])-2] = '\0';
            strchr(lowerArg,',')[0] = '\0';

            yStart = atof(num1);
            yEnd = atof(num2);
        }
        else if(strcmp(lowerArg, "-i") == 0 || strcmp(lowerArg, "--iter") == 0 || strcmp(lowerArg, "--iters") == 0 || strcmp(lowerArg, "--iterations") == 0 || strcmp(lowerArg, "--max-iter") == 0 || strcmp(lowerArg, "--max-iters") == 0 || strcmp(lowerArg, "--max-iterations") == 0 || strcmp(lowerArg, "--max-i") == 0 || strcmp(lowerArg, "--m-i") == 0 || strcmp(lowerArg, "--m-iter") == 0 || strcmp(lowerArg, "--m-iters") == 0 || strcmp(lowerArg, "--m-iterations") == 0 || strcmp(lowerArg, "--mi") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0xE;
            }

            max_iteration = atoi(argv[i]);

            if(max_iteration == 0)
            {
                return 0xF;
            }
        }
        else if(strcmp(lowerArg, "-d") == 0 || strcmp(lowerArg, "--delim") == 0 || strcmp(lowerArg, "--deliminator") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x10;
            }

            deliminator = argv[i][0];
            if(deliminator == '\\')
            {
                if(argv[i][1] == 'n' || argv[i][1] == 'N')
                {
                    deliminator = '\n';
                }
                else if(argv[i][1] == 't' || argv[i][1] == 'T')
                {
                    deliminator = '\t';
                }
                else
                {
                    return 0x11;
                }
            }
        }
        else if(strcmp(lowerArg, "-mtm") == 0 || strcmp(lowerArg, "--mt-mode") == 0 || strcmp(lowerArg, "--multithreading-mode") == 0 || strcmp(lowerArg, "--multi-threading-mode") == 0 || strcmp(lowerArg, "--multithread-mode") == 0 || strcmp(lowerArg, "--multi-thread-mode") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x12;
            }
            lowerArg = strlwr(argv[i]);

            if(strcmp(lowerArg, "split") == 0)
            {
                multiThreadingMode = AutoSplit;
            }
            else if(strcmp(lowerArg, "start") == 0)
            {
                multiThreadingMode = AutoStart;
            }
            else
            {
                return 0x13;
            }
        }
        else if(strcmp(lowerArg, "-t") == 0 || strcmp(lowerArg, "--threads") == 0 || strcmp(lowerArg, "--use-threads") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x14;
            }

            useThreads = atoi(argv[i]);
        }
        else if(strcmp(lowerArg, "-rt") == 0 || strcmp(lowerArg, "--r-threads") == 0 || strcmp(lowerArg, "--reserved-threads") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x15;
            }

            reservedThreads = atoi(argv[i]);
        }
        else if(strcmp(lowerArg, "--test") == 0 || strcmp(lowerArg, "--testing") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x16;
            }
            lowerArg = strlwr(argv[i]);

            if((lowerArg[0] == 'o' && lowerArg[1] == 'n') || lowerArg[0] == 't' || lowerArg[0] == 'y' || lowerArg[0] == '1')
            {
                testing = true;
            }
            else if((lowerArg[0] == 'o' && lowerArg[1] == 'f') || lowerArg[0] == 'f' || lowerArg[0] == 'n' || lowerArg[0] == '0')
            {
                testing = false;
            }
            else
            {
                return 0x17;
            }
        }
        else if(strcmp(lowerArg, "-xcw") == 0 || strcmp(lowerArg, "--x-center-w") == 0 || strcmp(lowerArg, "--x-center-width") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x18;
            }
            lowerArg = strlwr(argv[i]);

            char *num1 = lowerArg;
            char *num2 = (&(strchr(lowerArg,',')[1]));

            strchr(lowerArg,',')[0] = '\0';

            floatingPoint center = atof(num1);
            floatingPoint magnitude = atof(num2);

            if(magnitude == 0.0)
            {
                return 0x19;
            }

            xStart = center - magnitude/2;
            xEnd = center + magnitude/2;

            changeXStart = false;
            changeXEnd = false;
        }
        else if(strcmp(lowerArg, "-ych") == 0 || strcmp(lowerArg, "--y-center-h") == 0 || strcmp(lowerArg, "--y-center-height") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x1A;
            }
            lowerArg = strlwr(argv[i]);

            char *num1 = lowerArg;
            char *num2 = (&(strchr(lowerArg,',')[1]));

            strchr(lowerArg,',')[0] = '\0';

            floatingPoint center = atof(num1);
            floatingPoint magnitude = atof(num2);

            if(magnitude == 0.0)
            {
                return 0x1B;
            }

            yStart = center - magnitude/2;
            yEnd = center + magnitude/2;

            changeYStart = false;
            changeYEnd = false;
        }
        else if(strcmp(lowerArg, "-jx") == 0 ||
                strcmp(lowerArg, "-jxc") == 0 ||
                strcmp(lowerArg, "--jx-center") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x1C;
            }

            lowerArg = strlwr(argv[i]);

            char *num = lowerArg;

            jx = atof(num);

        }
        else if(strcmp(lowerArg, "-jy") == 0 ||
                strcmp(lowerArg, "-jyc") == 0 ||
                strcmp(lowerArg, "--jy-center") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x1D;
            }

            lowerArg = strlwr(argv[i]);

            char *num = lowerArg;

            jy = atof(num);
        }
        else if(strcmp(lowerArg, "-jp") == 0 ||
                strcmp(lowerArg, "-jpower") == 0 ||
                strcmp(lowerArg, "--j-power") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x1E;
            }

            lowerArg = strlwr(argv[i]);

            char *num = lowerArg;

            jp = atof(num);
        }
        else if(strcmp(lowerArg, "-pw") == 0 ||
                strcmp(lowerArg, "-pwidth") == 0 ||
                strcmp(lowerArg, "-pixw") == 0 ||
                strcmp(lowerArg, "-pixelw") == 0 ||
                strcmp(lowerArg, "-pixwidth") == 0 ||
                strcmp(lowerArg, "--pixel-width") == 0 ||
                strcmp(lowerArg, "--pix-width") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x1F;
            }

            lowerArg = strlwr(argv[i]);

            char *num = lowerArg;

            pixelWidth = atoi(num);
        }
        else if(strcmp(lowerArg, "-ph") == 0 ||
                strcmp(lowerArg, "-pheight") == 0 ||
                strcmp(lowerArg, "-pixh") == 0 ||
                strcmp(lowerArg, "-pixelh") == 0 ||
                strcmp(lowerArg, "-pixheight") == 0 ||
                strcmp(lowerArg, "--pixel-height") == 0 ||
                strcmp(lowerArg, "--pix-height") == 0)
        {
            i++;
            if(i >= argc)
            {
                return 0x20;
            }

            lowerArg = strlwr(argv[i]);

            char *num = lowerArg;

            pixelHeight = atoi(num);
        }
        else
        {
            return 0x21;
        }
    }

    if(changeXStart)
    {
        xStart += xSpacing;
    }
    if(changeXEnd)
    {
        xEnd -= xSpacing;
    }
    if(changeYStart)
    {
        yStart += xSpacing;
    }
    if(changeYEnd)
    {
        yEnd -= xSpacing;
    }

    if(piping)
    {
        _setmode( _fileno( stdin ), _O_BINARY );
        _setmode( _fileno( stdout ), _O_BINARY );
    }
    else
    {
        cout << "Working Memory." << endl;
    }

    storageSizeInBytes = 3;

    xRoundDigits = ceil(log10(1/xSpacing));
    xSpacingRoundHelper0 = pow(.1,xRoundDigits);
    xSpacingRoundHelper1 = pow(10,xRoundDigits);
    xSpacingRoundHelper2 = xSpacing*xSpacingRoundHelper1;
    xSpacingRoundHelper3 = xSpacingRoundHelper0*xSpacingRoundHelper2;
    xSpacingRoundHelper4 = xSpacingRoundHelper1/(xSpacingRoundHelper2);

    yRoundDigits = ceil(log10(1/ySpacing));
    ySpacingRoundHelper0 = pow(.1,yRoundDigits);
    ySpacingRoundHelper1 = pow(10,yRoundDigits);
    ySpacingRoundHelper2 = ySpacing*ySpacingRoundHelper1;
    ySpacingRoundHelper3 = ySpacingRoundHelper0*ySpacingRoundHelper2;
    ySpacingRoundHelper4 = ySpacingRoundHelper1/(ySpacingRoundHelper2);

    xStart = xSpacingRound(xStart);
    yStart = ySpacingRound(yStart);
    xEnd = xSpacingRound(xEnd);
    yEnd = ySpacingRound(yEnd);

    storageType xs = (storageType)((xEnd-xStart)/xSpacing);
    storageType ys = (storageType)((yEnd-yStart)/ySpacing);

    if(pixelWidth != 0)
    {
        while(xs < pixelWidth)
        {
            xEnd = xSpacingRound(xEnd + xSpacing);
            xs = (storageType)((xEnd-xStart)/xSpacing);
        }
        while(xs > pixelWidth)
        {
            xEnd = xSpacingRound(xEnd - xSpacing);
            xs = (storageType)((xEnd-xStart)/xSpacing);
        }
    }

    if(pixelHeight != 0)
    {
        while(ys < pixelHeight)
        {
            yEnd = ySpacingRound(yEnd + ySpacing);
            ys = (storageType)((yEnd-yStart)/ySpacing);
        }
        while(ys > pixelHeight)
        {
            yEnd = ySpacingRound(yEnd - ySpacing);
            ys = (storageType)((yEnd-yStart)/ySpacing);
        }
    }

    xs = round(xs);
    ys = round(ys);

    uint64_t totalPixels = (xs+1) * (ys+1);

    Pixel **image = (Pixel**)malloc(sizeof(Pixel*)*totalPixels);
    while(!image) //while it points to null
    {
        image = (Pixel**)malloc(sizeof(Pixel*)*totalPixels);
    }

    uint64_t currentPix = 0;
    for(floatingPoint y = yEnd; y >= yStart; y = ySpacingRound(y-ySpacing))
    {
        for(floatingPoint x = xStart; x<= xEnd; x = xSpacingRound(x+xSpacing))
        {
            image[currentPix] = (Pixel*)malloc(sizeof(Pixel));
            while(!image[currentPix]) //while it points to null
            {
                image[currentPix] = (Pixel*)malloc(sizeof(Pixel));
            }

            image[currentPix]->f1 = x;
            image[currentPix]->f2 = y;
            currentPix++;
        }
    }

    if(!piping)
    {
        cout << "Starting." << endl;
    }

    MultiThreading calculationThreads = MultiThreading(renderPixel, (void**)image, totalPixels);

    if(useThreads == 0)
    {
        calculationThreads.reduceThreadCount(reservedThreads);
    }
    else
    {
        calculationThreads.setThreadCount(useThreads);
    }

    switch(multiThreadingMode)
    {
    case AutoSplit:
        calculationThreads.autoSplit();
        break;
    case AutoStart:
        calculationThreads.autoStart();
        break;
    default:
        calculationThreads.autoSplit();
        break;

    //MultiThreading calculationThreads = MultiThreading(renderPixel, (void**)image, totalPixels);//why?
    }

    if(!piping)
    {
        cout << "Generating Histogram." << endl;
    }

    ///Histogram starts here
    int highestIteration = 0;

    for(uint64_t pix = 0; pix < totalPixels; pix++)
    {
        if(isnan(image[pix]->f1))
        {
            continue;
        }
        int flooredIterationCount = (int)floor(image[pix]->f1);
        if(flooredIterationCount>highestIteration)
        {
            highestIteration = flooredIterationCount;
        }
    }

    uint64_t *histogram = (uint64_t*)malloc(sizeof(uint64_t)*(highestIteration+1));
    while(!histogram)//while it points to null
    {
        histogram = (uint64_t*)malloc(sizeof(uint64_t)*(highestIteration+1));
    }

    for(int i = 0; i <= (int)highestIteration; i++)
    {
        histogram[i] = 0;
    }

    for(uint64_t pix = 0; pix < totalPixels; pix++)
    {
        if(isnan(image[pix]->f1))
        {
            continue;
        }
        histogram[(int)floor(image[pix]->f1)]++;
    }

    uint64_t histogram_total = 0;

    for(int i = 0; i <= highestIteration; i++)
    {
        histogram_total += histogram[i];
    }

    for(uint64_t pix = 0; pix < totalPixels; pix++)
    {
        image[pix]->histogram = histogram;
        image[pix]->histogram_total = histogram_total;
    }

    maxHue = getHue(highestIteration, histogram, histogram_total);

    MultiThreading coloringThreads = MultiThreading(huePalette, (void**)image, totalPixels);

    if(useThreads == 0)
    {
        coloringThreads.reduceThreadCount(reservedThreads);
    }
    else
    {
        coloringThreads.setThreadCount(useThreads);
    }

    coloringThreads.autoSplit();

    if(!piping)
    {
        cout << "Done!" << endl;

        cout << "You have calculated " << totalPixels << " pixels." << endl;
    }
    else
    {
        for(uint64_t pix = 0; pix < totalPixels; pix++)
        {
            printIter(image[pix]);
        }
    }

    for(uint64_t pix = 0; pix < totalPixels; pix++)
    {
        free(image[pix]);
        image[pix] = nullptr;
    }

    free(image);
    image = nullptr;

    if(!piping)
    {
        cout << "Exiting." << endl;
    }

    return 0;
}
