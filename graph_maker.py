import matplotlib.pyplot as plt

def avg(tmplist):
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

if __name__ == '__main__':
    st1 = "tus"
    st2 = "dma"

    wb1 = []
    wb2 = []

    with open(st1+'19502023.txt') as f:
        for i in range(74):
            wb1.append(float(f.readline()))

    with open(st2+'19502023.txt') as f:
        for i in range(74):
            wb2.append(float(f.readline()))

    difs = [wb1[i] - wb2[i] for i in range(74)]
    smoothvals = smooth(difs, 11)

    years = [x for x in range(1950, 2024)]
    smoothyrs = [x for x in range(1955, 2019)]


    plt.plot(years, difs)
    plt.plot(smoothyrs, smoothvals)
    plt.show()

    
