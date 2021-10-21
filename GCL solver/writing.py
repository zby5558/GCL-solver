#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 17:47:10 2021

@author: boyang
"""

def write(fileName, hp, sendOff, openTime, closeTime,host,period,dest,queue,size,flowID,switch,port, linkList, link):
    f = open(fileName, "a+")
    f.write('<?xml version="1.0" ?>'+'\n')
    f.write('<schedules>'+'\n')
    f.write('     <defaultcycle>'+str(hp)+'us</defaultcycle>'+"\n")
    for i in range(len(sendOff)):
        temp = sendOff[i][0]
        flag = 1
        for j in range(len(sendOff[i])):
            if(sendOff[i][j] != temp):
                flag = 0
        if(len(sendOff[i]) == 1 or flag == 1):
            str1 = '     <host name="'+host[i]+'">'+"\n"
            str2 = '          <cycle>'+str(period[i]*1000000)+'us</cycle>'+"\n"
            f.write(str1)
            f.write(str2)
            f.write('          <entry>'+"\n")
            f.write('               <start>'+str(sendOff[i][0])+'us</start>'+"\n")
            f.write('               <queue>'+queue[i]+'</queue>'+"\n")
            f.write('               <dest>'+dest[i]+'</dest>'+"\n")
            f.write('               <size>'+str(size[i]/8)+'B</size>'+"\n")
            f.write('               <flowId>'+str(flowID[i])+'</flowId>'+"\n")
            f.write('          </entry>'+"\n")
            f.write('     </host>'+"\n")
        else:
            for j in range(len(sendOff[i])):
                str1 = '     <host name="'+host[i]+'">'+"\n"
                str2 = '          <cycle>'+str(period[i]*1000000*len(sendOff[i]))+'us</cycle>'+"\n"
                f.write(str1)
                f.write(str2)
                f.write('          <entry>'+"\n")
                f.write('               <start>'+str(sendOff[i][j]+j*period[i]*1000000)+'us</start>'+"\n")
                f.write('               <queue>'+queue[i]+'</queue>'+"\n")
                f.write('               <dest>'+dest[i]+'</dest>'+"\n")
                f.write('               <size>'+str(size[i]/8)+'B</size>'+"\n")
                f.write('               <flowId>'+str(flowID[i])+'</flowId>'+"\n")
                f.write('          </entry>'+"\n")
                f.write('     </host>'+"\n")
                
    for i in range(len(openTime)):
        
        str1 = '     <switch name="'+switch[i]+'">'+"\n"
        str2 = '          <port id="'+port[i]+ '">'+"\n"
        str3 = '               <schedule cycleTime="'+str(hp)+ 'us">'+"\n"
        f.write(str1)
        f.write(str2)
        f.write(str3)
        prevClose = 0
        for j in range(len(openTime[i])):
            
            if(openTime[i][j]>prevClose):
                str2 = '                         <length>'+str(openTime[i][j]-prevClose)+'us</length>'+'\n'
                str3 = '                         <bitvector>00000000</bitvector>'+'\n'
                f.write('                    <entry>'+"\n")
                f.write(str2)
                f.write(str3)
                f.write('                    </entry>'+"\n")
            str2 = '                         <length>'+str(closeTime[i][j]-openTime[i][j])+'us</length>'+'\n'
            str3 = '                         <bitvector>11111111</bitvector>'+'\n'
            prevClose = closeTime[i][j]
            f.write('                    <entry>'+"\n")
            f.write(str2)
            f.write(str3)
            f.write('                    </entry>'+"\n")
        if(prevClose<hp):
            str2 = '                         <length>'+str(hp-prevClose)+'us</length>'+'\n'
            str3 = '                         <bitvector>00000000</bitvector>'+'\n'
            f.write('                    <entry>'+"\n")
            f.write(str2)
            f.write(str3)
            f.write('                    </entry>'+"\n")    
        str1 = '               </schedule>'+"\n"
        str3 = '     </switch>'+"\n"
        str2 = '          </port>'+"\n"
        f.write(str1)
        f.write(str2)
        f.write(str3)
    f.write('</schedules>')       
    f.close()
    
    
def writingExpectedWindow(offsets,openTime,closeTime,link,linkList,flowID,switch,res):
    for i in range(len(offsets)):
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
            f.close()
    