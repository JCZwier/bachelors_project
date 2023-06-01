import random
import numpy as np

#parameters we implement throughout the analysis unless changes to them are made
c = 15
n = 1000
a = 1
p = .05
N = 1000 
m = 50

#citation network class
class node():
    def __init__(self):
        self.inDegree = 0
        self.inDegList = []
        self.outDegList = []
    def increment(self, x):
        self.inDegree += x
    def listAdd(self):
        self.inDegList.append(self.inDegree)
    def outDegAdd(self, y):
        self.outDegList.append(y)
        
#method for constructing the citation network
#Implement Prices model using the breakdown of the citation probability
def createNetworkSamplingWithRep(c, a, n):#this is the one we use, when c is deterministic 
    network = []
    samplingList = []
    nodeList = []
    prob = c/float(c+a)
    for i in range(1, n+1):
        newPaper = node()
        network.append(newPaper)
        tempList = []
        if i != 1:
            for j in range(0, c): #make all c citations 
                if samplingList: #make sure sampling list is non-empty
                    if random.uniform(0,1) <= prob: 
                        s = random.choice(samplingList) #choose from samplingList uniformly, preferential attachment
                        tempList.append(s)
                        network[i-1].outDegAdd(s)
                        network[s-1].increment(1)
                        #network[s-1].listAdd()
                    else:
                        k = random.choice(nodeList) #else sample from the node list
                        tempList.append(k)
                        network[i-1].outDegAdd(k)
                        network[k-1].increment(1)
                else:
                    k = random.choice(nodeList)
                    tempList.append(k)
                    network[i-1].outDegAdd(k)
                    network[k-1].increment(1)
                    #network[k-1].listAdd()
            samplingList.extend(tempList)

        for j in range(0, i):
            network[j].listAdd()
        nodeList.append(i)

    return network
    
#this is the easier and less convoluted way to do this
#use this to collect the m papers which define a "synthetic" author
def generateRandList_uni(n, m):
    return np.random.choice(n, m)

func = generateRandList_uni(4, 9)
print(func)
