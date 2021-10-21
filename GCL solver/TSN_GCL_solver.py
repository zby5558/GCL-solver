# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 18:09:04 2021

@author: zby09
"""
import math
import copy
import writing
from gekko import GEKKO  
import os
m = GEKKO(remote=False)
m.options.SOLVER = 1

cwd = os.getcwd()
dirName = '/testGCL' # the name of the folder where you want to store the output
fileName1 = "testGCL" # The name of two requried files should be fileName1+Pattern.txt and fileName1+Link.txt
f = open(fileName1+"Pattern.txt", "r")
#f = open("oneSwitchTest.txt", "r")
flowID = []
period = []
size = []
path = []
offset = []
delayReq = []
jitterReq = []
switch = []
port = []
host = []
dest = []
hp = 0
delta = 0
queue = []
for line in f.readlines():
    if(line.startswith("FlowID")):
        flowID.append(int(line.split(" ")[1]))
    if(line.startswith("Period")):
        period.append(float(line.split(" ")[1])/1000)
    if(line.startswith("Size")):
        size.append(float(line.split(" ")[1])*8)
    if(line.startswith("Path")):
        path.append(line.split(" ")[1].replace("\n",""))
    if(line.startswith("Hyperperiod")):
        hp = (float(line.split(" ")[1].replace("\n",""))/1000)
    if(line.startswith("Delay-")):
        delayReq.append(float(line.split(" ")[1].replace("\n",""))/1000)
    if(line.startswith("Jitter-")):
        jitterReq.append(float(line.split(" ")[1].replace("\n",""))/1000)
    if(line.startswith("Host")):
        host.append(line.split(" ")[1].replace("\n",""))
    if(line.startswith("Dest")):
        dest.append(line.split(" ")[1].replace("\n",""))
    if(line.startswith("Que")):
        queue.append(line.split(" ")[1].replace("\n",""))
f.close()


link = []
speed = []
delay = []
f = open(fileName1+"Link.txt", "r")
#f = open("oneSwitchLink.txt", "r")
for line in f.readlines():
    if(line.startswith("Link")):
        link.append(line.split(" ")[1].replace("\n",""))
    if(line.startswith("Speed")):
        speed.append(float(line.split(" ")[1].replace("\n",""))*1000000)
    if(line.startswith("Delay")):
        delay.append(float(line.split(" ")[1].replace("\n",""))/1000)
    if(line.startswith("Switch")):
        switch.append(line.split(" ")[1].replace("\n",""))
    if(line.startswith("Port")):
        port.append(line.split(" ")[1].replace("\n",""))
f.close()

linkList = []
offsets = []
dstOffsets = []
for i in range(len(flowID)):
    nodes = path[i].split("-")
    tempL = []
    for j in range(len(nodes)-1):
       tempL.append(nodes[j]+"-"+nodes[j+1])
    linkList.append(tempL)
    offsets.append([])
    dstOffsets.append([])
    
for i in range(len(dstOffsets)):
    for j in range(int(hp/period[i])):
        dstOffsets[i].append(0)
        dstOffsets[i][j] = m.Var()
        dstOffsets[i][j].lower = 0
    
for i in range(len(flowID)):
    for j in range(len(linkList[i])):
        offsets[i].append([])

for i in range(len(offsets)):
    for j in range(len(offsets[i])):
        numFrames = int(hp/period[i])
        for k in range(numFrames):
            offsets[i][j].append(0)

dic = {}

for i in range(len(link)):
    tempL = []
    for j in range(len(linkList)):
        if(link[i] in linkList[j]):
            tempL.append(j)
    dic[link[i]]=tempL

#Frame Constraint
for i in range(len(offsets)):
    for j in range(len(offsets[i])):
        for k in range(len(offsets[i][j])):
            offsets[i][j][k] = m.Var()
            ind = link.index(linkList[i][j])#i is the flow, j is the link, and is  the kth frame in the hyperperiod
            offsets[i][j][k].lower = 0
           # m.Equation(offsets[i][j][k]/1000000<=period[i]-size[i]/speed[ind])
            if(j == 0):
                m.Equation(offsets[i][j][k]/1000000<=jitterReq[i])
            else:
                m.Equation(offsets[i][j][k]/1000000<=period[i]-size[i]/speed[ind])
#Link Constraint
prevTested = []

for i in range(len(offsets)):    
    for j in range(len(offsets[i])):        
        for k in range(len(offsets[i][j])):
            for i1 in range(i+1,len(offsets)):
                if(linkList[i][j] in linkList[i1]):
                    str1 = str(flowID[i])+'-'+str(flowID[i1])+'-'+linkList[i][j]
                    if(not str1 in prevTested):
                        prevTested.append(str1)
                    else:
                        continue
                    ind = linkList[i1].index(linkList[i][j])
                    for k1 in range(len(offsets[i1][j])):
                        for alpha in range(int(hp/period[i])):
                            for beta in range(int(hp/period[i1])):
                                ind1 = link.index(linkList[i][j])#
                                m.Equation(offsets[i][j][k]/1000000+alpha*period[i]-offsets[i1][ind][k1]/1000000-beta*period[i1]-size[i1]/speed[ind1]>=0)

#Flow Transmission Constraint
for i in range(len(offsets)):    
    for j in range(1,len(offsets[i])):        
        for k in range(len(offsets[i][j])): 
            ind = link.index(linkList[i][j-1])
            m.Equation(offsets[i][j][k]/1000000-delay[ind]-delta-offsets[i][j-1][k]/1000000-size[i]/speed[ind]>=0)    
for i in range(len(offsets)):
    ind = link.index(linkList[i][len(linkList[i])-1])
    for k in range(len(dstOffsets[i])):
        m.Equation(dstOffsets[i][k]/1000000-offsets[i][len(linkList[i])-1][k]/1000000-delay[ind]-delta-size[i]/speed[ind]>=0) 

#End-to-End Contraint
for i in range(len(offsets)):
    ind = link.index(linkList[i][len(linkList[i])-1])
    for k in range(len(dstOffsets[i])):
        m.Equation(dstOffsets[i][k]/1000000+size[i]/speed[ind]-offsets[i][0][k]/1000000<=delayReq[i])
                         
#Frame Isolation Constraint

for i in range(len(offsets)):    
    for j in range(len(offsets[i])):        
        for k in range(len(offsets[i][j])):
            dstLink = linkList[i][j].split('-')[1]
            nextLinks = []
            for l in link:
                if(dstLink == l.split('-')[0]):
                    nextLinks.append(l)
            for i1 in range(i+1,len(offsets)):
                for l in range(len(linkList[i])):
                    if(linkList[i][l] in nextLinks):
                        for alpha in range(int(hp/period[i])):
                                for beta in range(int(hp/period[i1])):      
                                    for k1 in range(len(offsets[i1][l])):
                                        ind1 = link.index(linkList[i][j])#
                                        m.Equation(offsets[i][j][k]/1000000+alpha*period[i]+delay[ind1]-offsets[i1][l][k1]/1000000-beta*period[i1]-delta>=0)

m.Obj(1)
m.solve()

res = []
sendOff = []
for i in range(len(offsets)):
    res.append([])
    sendOff.append([])
    for j in range(len(offsets[i])):
        if(j == 0):
            for k in range(len(offsets[i][j])):
                sendOff[i].append(offsets[i][j][k].value[0])
        else:
            res[i].append([])
            for k in range(len(offsets[i][j])):
                res[i][j-1].append(offsets[i][j][k].value[0]+k*period[i]*1000000)
openTime = [];
closeTime = [];
for i in range(len(link)):
    openTime.append([])
    closeTime.append([])
for i in range(len(offsets)):
    for j in range(len(offsets[i])):
        if(j == 0):
            continue
        ind = link.index(linkList[i][j])
  #      print("link index"+str(ind))
        for k in range(len(offsets[i][j])):
            openTime[ind].append(res[i][j-1][k])
            closeTime[ind].append(res[i][j-1][k]+size[i]*1000000/speed[i])

for i in range(len(link)):
    openTime[i].sort()
    closeTime[i].sort()
for i in range(len(link)):
    j = 0;
    while(j<len(closeTime[i])-1):
        if(closeTime[i][j] == openTime[i][j+1]):
            del closeTime[i][j]
            del openTime[i][j+1]
            j=j-1
        j = j+1
hp = hp*1000000
os.chdir(cwd+dirName);
writing.write(fileName1+".xml", hp, sendOff, openTime, closeTime,host,period,dest,queue,size,flowID,switch,port, linkList, link)
writing.writingExpectedWindow(offsets,openTime,closeTime,link,linkList,flowID,switch,res)

fileName = fileName1+"Routing.xml"
mapLinktoSwitch = {}
for i in range(len(link)):
    if(switch[i] != 'Null'):
        if(not switch[i] in mapLinktoSwitch):
            temp = []
            temp.append(link[i])
            mapLinktoSwitch[switch[i]] = temp
        else:
            temp = mapLinktoSwitch[switch[i]]
            temp.append(link[i])
            mapLinktoSwitch[switch[i]] = temp
f = open(fileName,"a+")
f.write('<filteringDatabases>'+'\n')
switch = set(switch)
switch = list(switch)
for i in range(len(switch)):
    if(switch[i] == 'Null'):
        continue

    f.write("	<filteringDatabase id="+'"'+switch[i]+'"'+">"+'\n')
    f.write("	    <static>"+'\n')
    f.write("	        <forward>"+'\n')
    temp = mapLinktoSwitch[switch[i]]
    print(temp)
    for j in range(len(temp)):
        ind = link.index(temp[j])
        portString = port[ind]
        for k in range(len(flowID)):
            if(temp[j] in linkList[k]):
                print('portString: '+str(portString))
                f.write("	        	<individualAddress macAddress="+'"'+dest[k]+'"'+" port="+'"'+str(portString)+'"'+" />"+"\n")
    f.write("	        </forward>"+'\n')
    f.write("	    </static>"+'\n')
    f.write("	</filteringDatabase>"+'\n')

f.write("</filteringDatabases>") 
f.close()
os.chdir(cwd)
    
'''for i in range(len(offsets)):
    for j in range(len(offsets[i])):
        if( j == 0):
            continue
        ind = link.index(linkList[i][j]) #find the link index
        fileName = "flowId"+str(flowID[i])+switch[ind]+".txt"
        f = open(fileName, "a+")
        f.write("Number-of-seq: "+str(len(offsets[i][j]))+'\n')
        for k in range(len(offsets[i][j])):
            prevClose = 0
            numWin = 0;
            for l in range(len(openTime[ind])):
                if(openTime[ind][l]>prevClose):
                    numWin = numWin+1;
                    prevClose = openTime[ind][l]
                numWin = numWin+1
                if(res[i][j-1][k]>=openTime[ind][l] and res[i][j-1][k]<closeTime[ind][l]):
                    f.write("Seq-"+str(k)+": "+str(numWin-1)+'\n')
                    break
        f.close()'''
    

