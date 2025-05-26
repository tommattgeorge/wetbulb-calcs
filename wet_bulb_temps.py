
import math
import matplotlib.pyplot as plt

def calcPres(b, j, k):
    M = 0.0289644
    G = 9.80665
    R = 8.31432
    e = -0.0065
    i = 0.0
    return b * (math.pow((k / (k + (e * (j - i)))), ((G * M) / (R * e))))
    
    
def simplePres(p, alt, t):
    M = 0.0289644
    G = 9.80665
    R = 8.31432
    return p*(math.exp(-M*G*alt/(R*(t+273.15))))

def avg(tmplist):
    if(len(tmplist) == 0): return 0.0 
    sum = 0.0
    for i in range(len(tmplist)):
        sum += tmplist[i]
    sum /= len(tmplist)
    return sum

def smooth(tmplist, window):
    newlist = []
    for i in range(len(tmplist)-window+1):
        newlist.append(avg(tmplist[i:i+window]))
    return newlist 

def esubs(Ctemp):
    Es = 6.112 * (2.718281828**(17.67 * Ctemp / (Ctemp + 243.5)))
    return Es
    
    
def invertedRH(Es, rh):
    E = Es * (rh/100)
    return E

def trim5(tmplist):
    count = 0
    for i in range(len(tmplist)) :
        if (tmplist[i] < 5.00):
            tmplist[i] = 5.00
            count+=1	

    

def wetbulb(Edifference, Twguess, Ctemp, MBpressure, E2, previoussign, incr):
    while (abs(Edifference) > 0.005):
        Ewguess = 6.112 * math.exp((17.67 * Twguess) / (Twguess + 243.5))
        Eguess = Ewguess - MBpressure * (Ctemp - Twguess) * 0.00066 * (1 + (0.00115 * Twguess))
        Edifference = E2 - Eguess
        if (Edifference == 0.0):
            incr = 0.0
        else:
            if (Edifference < 0):
                cursign = -1
                if (cursign != previoussign):
                    previoussign = cursign
                    incr = incr / 10
                else: 
                    incr = incr
                
            else: 
                cursign = 1
                if (cursign != previoussign) :
                    previoussign = cursign
                    incr = incr / 10
                else:
                    incr = incr
                
            
        
        Twguess = Twguess + incr * previoussign
    
    wetbulb = Twguess - incr * previoussign # Thanks BruceZ
    return wetbulb
    
    
def oldwetbulb(T, RH):
    Tw = T * math.atan(0.151977 * math.sqrt(RH + 8.313659)) + math.atan(T + RH) \
    - math.atan(RH - 1.676331) + 0.00391838 * math.pow(RH, 1.5) * math.atan(0.023101 * RH) \
    - 4.686035
    return Tw
    

def process(inputFile, type, start, end):
    retlist = []
    tmplist = [1]
    curyear = start

    with open(inputFile, 'r') as f:
        f.readline()
        strt = f.readline()


        prevtime = 23

        while (strt != ""):
            stt = strt.split()
            date = stt[1]
            year = date[0:4]
            if (int(year) < start or int(year) > end):
                strt = f.readline()
                continue
            
            if int(year) > curyear:
                retlist.append(tmplist.copy())
                for i in range(curyear+1, int(year)):
                    retlist.append([])
                curyear = int(year)
                tmplist = [1]

            time = stt[2]
            if (int(time[len(time) - 5: len(time) - 3]) == (prevtime + 1) % 24):
                stmp = ""
                for i in range(type+1):
                    stmp = stt[3+i]
                
                tmp = -100.0
                if (stmp != "M"):
                    tmp = float(stmp)
                
                tmplist.append(tmp)
                prevtime = (prevtime + 1) % 24
            elif (int(time[len(time) - 5: len(time) - 3]) == (prevtime) % 24):
                stmp = ""
                for i in range(type+1):
                    stmp = stt[3+i]
                
                tmp = -100.0
                if (stmp != "M"):
                    tmp = float(stmp)
                    tmplist[-1] = tmp
                
            else:
                newtime = int(time[len(time) - 5: len(time) - 3])
                extime = newtime
                if (newtime < prevtime):
                    extime = newtime + 24
                
                for xx in range(prevtime+1, extime):
                    tmplist.append(-100.0)
                
                stmp = ""
                for i in range(type+1):
                    stmp = stt[3+i]
                
                tmp = -100.0
                if (stmp != "M"):
                    tmp = float(stmp)
                
                tmplist.append(tmp)
                prevtime = newtime
            
            strt = f.readline()
        
        retlist.append(tmplist.copy())
        return retlist
    
def modify(tmplist, type):
    if(len(tmplist) == 0): return
    dfl = 10.0
    if(type == 1): dfl = 50.0
    if(type == 2): dfl = 1013.25
    lastt = tmplist[0]
    if(lastt  < -50.0): lastt = dfl
    i = 0
    while(i< len(tmplist)):
        if (tmplist[i]  < -50.0):
            origin = i
            while (i<len(tmplist)-1 and tmplist[i] < -50.0):
                i+=1
            
            if(tmplist[i]  < -50.0): tmplist[i] = dfl
            delta = (tmplist[i] - lastt) / (i - origin + 1)
            for z in range(i - origin):
                tmplist[z + origin] = lastt + delta * (z + 1)
            
            if(i == len(tmplist) - 1): i+=1
        else:
            lastt = tmplist[i]
            i+=1

def computeAvg(readFile, alt, oldwetbulbbool, start, end):
    tmplist = process(readFile, 0, start, end)
    humlist = process(readFile, 1, start, end)
    slplist = process(readFile, 2, start, end)
        
    if (len(tmplist) == 0):
        ret = []
        for i in range(end+1-start):
            tmp = [0,0,0]
            tmp[0] = -100.0
            tmp[1] = -100.0
            tmp[2] = -100.0
            ret.append(tmp.copy())
        return ret
        
    for i in range(end+1-start):    
        modify(tmplist[i], 0)
        modify(humlist[i], 1)
        modify(slplist[i], 2)

    realp = []
    for x in range(end+1-start): 
        realp.append([])    
        for i in range(len(tmplist[x])):
            realp[x].append(calcPres(100.0 * slplist[x][i], alt, 273.15 + tmplist[x][i]) / 100.0)
    
    wetbulblist = []

    for x in range(end+1-start):  
        wetbulblist.append([]) 
        for i in range(len(humlist[x])): 
            Ctemp = tmplist[x][i]
            RH = humlist[x][i]
            MBpressure = realp[x][i]
            Twguess = 0
            incr = 10
            previoussign = 1
            Edifference = 1
            Es = esubs(Ctemp)
            E2 = invertedRH(Es, RH)
            Tw = 0.0
            if(oldwetbulbbool):
                Tw = oldwetbulb(Ctemp, RH)
            
            else:
                Tw = wetbulb(Edifference, Twguess, Ctemp, MBpressure, E2, previoussign, incr)
            
            wetbulblist[x].append(Tw)
        
    ret = []
    for i in range(end+1-start):
        tmp = [-99,-99,-99]
        tmp[0] = avg(wetbulblist[i])*1.8+32
        tmp[1] = avg(tmplist[i])*1.8+32
        tmp[2] = avg(humlist[i])
        ret.append(tmp)

    return ret
    

def wet_bulb_temps():
    st1 = "tus"
    st2 = "ric"
    start = 1950
    rng = 73
    end = start + rng
    oldwetbulb = False
    writeToFile = True
    yearByYear = True
    doplot = False
    routineSpecials = True
    reportType = "" if routineSpecials else "routine"
    readFile1 = st1 + reportType + ".tsv"
    readFile2 = st2 + reportType + ".tsv"
        
    with open('altlist.txt', 'r') as f:
        altline = f.readline()
        alt1 = 0.0
        while(altline != ""):
            tokens = altline.split()
            if tokens[0] == st1:
                alt1 = float(tokens[1])
                break
            altline = f.readline()
    
    with open('altlist.txt', 'r') as f:
        altline = f.readline()
        alt2 = 0.0
        while(altline != ""):
            tokens = altline.split()
            if tokens[0] == st2:
                alt2 = float(tokens[1])
                break
            altline = f.readline()
    
    station1 = []
    station2 = []

    if (doplot):
        for z in range(start, end+1):	 
                    
            avgs1 = computeAvg(readFile1, alt1, oldwetbulb, z, z)
            avgs2 = computeAvg(readFile2, alt2, oldwetbulb, z, z)
                    
            station1.append(avgs1[0])                    
            station2.append(avgs2[0])                    

        years = [x for x in range(start, end+1)]
        difs = [station1[x] - station2[x] for x in range(end+1-start)]

        smoothyrs = [x for x in range(start+5, end-4)]
        smoothvals = smooth(difs, 11)

        plt.plot(years, difs)
        plt.plot(smoothyrs, smoothvals)
        plt.show()

    elif (yearByYear and writeToFile) :
        outputfile = "" + st1 + str(start) + str(end) + reportType + ".txt"
        with open(outputfile, 'w') as f:    
            # for z in range(start, end+1):
            #     if(z%10 == 0):
            #         avgs = computeAvg(readFile1, alt1, oldwetbulb, z, z+9)
            #         f.write(str(z) + "s :\n")
            #         f.write('\n')
            #         f.write(str(avgs[0])+'\n')
            #         f.write(str(avgs[1])+'\n')
            #         f.write(str(avgs[2])+'\n')
            #         f.write('\n')
            #         f.write('\n')
            
        
            avgs = computeAvg(readFile1, alt1, oldwetbulb, start, end)

            for z in range(end+1-start):
            
                if(avgs[z][0] < 47.0 or avgs[z][0] > 59.0): avgs[z][0] = 51.0

                # f.write(str(z) + ":\n")
                # f.write('\n')
                f.write(str(avgs[z][0])+'\n')
                # f.write(str(avgs[1])+'\n')
                # f.write(str(avgs[2])+'\n')
                # f.write('\n')
                # f.write('\n')
            
    elif (yearByYear and not writeToFile):
        for z in range(start, end+1):
            if (z%10 == 0):
                avgs = computeAvg(readFile1, alt1, oldwetbulb, z, z+9)
                print(str(z) + "s :")
                print()
                print(str(avgs[0]))
                print(str(avgs[1]))
                print(str(avgs[2]))
                print()
                print()
                
            
        for z in range(start, end+1):	 
                    
            avgs = computeAvg(readFile1, alt1, oldwetbulb, z, z)
                    
            if(avgs[0] < -50.0): continue
                    
            print(str(z) + ":")
            print()
            print(str(avgs[0]))
            print(str(avgs[1]))
            print(str(avgs[2]))
            print()
            print()
            
        
    else:

        avgs = computeAvg(readFile1, alt1, oldwetbulb, start, end)
            
        print(str(avgs[0]))
        print(str(avgs[1]))
        print(str(avgs[2]))

if __name__ == '__main__':
    wet_bulb_temps()
     



