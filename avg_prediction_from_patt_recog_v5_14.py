# based on Predicitions From Patterns: Machine Learning and Pattern Recognition for Forex and Stock Trading by Sentdex
# updated by Maroof Khan to make pattern logging, recognition more robust. Code significantly cleaned up.
# date: 02/01/2015

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.dates import strpdate2num
import matplotlib.dates as mdates
import numpy as np
from functools import reduce
import time

# to be used to calculate total program time required for completion
totalStart = time.time()

def bytedate2num(fmt):
    def converter(b):
        return mdates.strpdate2num(fmt)(b.decode('ascii'))
    return converter

# next two functions are to decode number string to date
date_converter = bytedate2num('%Y%m%d%H%M%S')

# 'GBPUSD1d.txt' is one days worth of forex data between US dollar and British pound
date,bid,ask = np.loadtxt('GBPUSD1d.txt', unpack=True,
                          delimiter=',',
                          converters = {0:date_converter})

def percentChange(startPoint, currentPoint):
    '''
    - calculate the percentage change between startPoint and currentPoint
    - pattern storage and pattern recognition functions will use this method
    '''
    # if method used in denominator this will ensure it is never zero
    try:
        x = ((float(currentPoint)-startPoint)/abs(float(startPoint)))*100.00
        if x == 0.0:
            return 0.0000000001
        else:
            return x
    except:
        return 0.0000000001
    
def patternStorage():
    '''
    - the method will update patternAr[]
    - pattern are judged to be the percentage change between from preceding to current point
    - 30 points in past are stored in above array
    - each element of patternAr[] is a list of length 30
    '''
    patStartTime = time.time()
    # last point of avgLine is for future comparison, we are collection patterns for 30 points
    # and have 30 points pass to estimate result
    x = len(avgLine) - 60

    y = 31
    while y < x:
        pattern = []
        cnt = 29
        while cnt > -1:
            p = percentChange(avgLine[y-30], avgLine[y-cnt])
            pattern.append(p)
            cnt -= 1

        outcomeRange = avgLine[y+20:y+30]
        currentPoint = avgLine[y]
        try:
            avgOutcome = reduce((lambda x, y: x+y), outcomeRange)/ len(outcomeRange)
        except Exception as e:
            print(str(e))
            avgOutcome = 0

        futureOutcome  = percentChange(currentPoint, avgOutcome)
        # store pattern in patternAr[]
        patternAr.append(pattern)
        # also put the performance futureOutput in performanceAr[]
        performanceAr.append(futureOutcome)
        y += 1

    patEndTime = time.time()
    
def currentPattern():
    '''
    - This is the current pattern that will be compared to all the historic ones
    - patterns are based on percentage change of current point to previous one
    - 30 point comparision of percentage change will be stored in list patForRec[]
    '''
    currPatStart = time.time()
    cnt = -30
    while cnt <= -1:
        cp = percentChange(avgLine[-31], avgLine[cnt])
        patForRec.append(cp)
        cnt += 1
    
def patternRecognition():
    
    patFound = 0 #boolean value of 1 if pattern found
    plotPatAr = []
    predictedOutcomesAr = []
    
    for eachPattern in patternAr:
        
        cnt = 0
        howSim = 0.0
        while cnt < 30:
            # how similar is present element pattern to a current one in patForRec[]?
            sim  = 100.00 - abs(percentChange(eachPattern[cnt],patForRec[cnt]))
            if sim > 30.0: #if pattern is 30% similar we are in business
                howSim = howSim + sim
                cnt += 1
            else:
                howSim = 0.0
                break

        howSim = howSim / 30.00
        if howSim > 70:
            patdex = patternAr.index(eachPattern)

            patFound = 1
            
            # 30 points in x-axis for plot
            xp = []
            for num in range(1,31):
                xp.append(num)

            # - we are looking through each pattern and if it is 'howSim' [how similar to current] we append it to array 'plotPatAr'
            plotPatAr.append(eachPattern)

    if patFound == 1:
        fig = plt.figure(figsize=(10,6))
        for eachPatt in plotPatAr:
            futurePoints = patternAr.index(eachPatt)

            if performanceAr[futurePoints] > patForRec[29]:
                pcolor = '#24bc00'
            else:
                pcolor = '#d40000'

            # we are adding each pattern to plot. eachPatt is already satisfying the howSim condition above
            plt.plot(xp,eachPatt)
            predictedOutcomesAr.append(performanceAr[futurePoints])
            # scatterplot of performance given on the side 
            plt.scatter(35, performanceAr[futurePoints], c = pcolor, alpha = .3)

        realOutcomeRange = allData[toWhat+20:toWhat+30]
        realAvgOutcome = reduce((lambda x, y: x+y), realOutcomeRange)/ len(realOutcomeRange)
        predictedAvgOutcome = reduce((lambda x, y: x+y), predictedOutcomesAr)/ len(predictedOutcomesAr)
        realMovement  = percentChange(allData[toWhat], realAvgOutcome)

        plt.scatter(40, realMovement, c = '#54fff7', s = 25)
        plt.scatter(40, predictedAvgOutcome, c = 'b', s = 25)

        plt.plot(xp, patForRec, '#54fff7', linewidth = 3)
        plt.grid(True)
        plt.title('''Pattern Recognition: Cyan bold curve is current curve. All others are similar by 70%.
                     Multiple points on show good outcome if blue and red if bad. For rightmost points: Dark blue is predicted avg outcome vs. cyan actual outcome''')
        plt.xlabel('elements in pattern array')
        plt.ylabel('Percent change of points on pattern')
        plt.text(3, 8, 'boxed italics text in data coords', style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
        plt.show()


dataLength = int(bid.shape[0])
#print('data length is: ', dataLength)

toWhat = 37000
allData = ((bid+ask)/2)

# loop through all methods from middle of data to the end of dataLength
while toWhat < dataLength:
    #store pattern from start of file to 'toWhat' for pattern storage and recognition
    avgLine = allData[:toWhat]

    patForRec = []
    patternAr = []
    performanceAr = []

    currentPattern()      
    patternStorage()
    patternRecognition()

    totalTime = time.time() - totalStart
    print('toWhat: ', toWhat)
    toWhat += 1
