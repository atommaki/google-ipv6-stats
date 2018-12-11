#!/usr/bin/python3

import urllib.request, urllib.error, urllib.parse
import re
import datetime
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv

response = urllib.request.urlopen('https://www.google.com/intl/en_ALL/ipv6/statistics/data/adoption.js')

datalineregex=re.compile('^ *\[20.., .*\],$')
timestamps=[]
data=[]
datamin=[]
dataavg=[]
datamax=[]
last7=[ 0, 0, 0, 0, 0, 0 ,0]
i=0
with open('results/results.csv', 'w') as f:
    wr = csv.writer(f)
    for line in response.read().splitlines():
        if datalineregex.match(line.decode("utf-8")):
            trans = dict.fromkeys(map(ord, '[] '), None) # to remove '[', ']', ' '
            datalist = line.decode("utf-8").translate(trans).split(',')
            wr.writerow(datalist)
            timestamps = timestamps+[ datetime.datetime(year=int(datalist[0]),month=int(datalist[1])+1,day=int(datalist[2])) ]
            last7[i]=float(datalist[3])
            if i == 6:
                i=0
            else:
                i=i+1
            #data=data+[ float(datalist[3]) ]
            datamin=datamin+[ min(last7) ]
            dataavg=dataavg+[ sum(last7)/7 ]
            datamax=datamax+[ max(last7) ]

logbase=2

fig, ax = plt.subplots()
ax.set_ylabel('log')
#ax2 = ax.twinx()

timestamps_num=mdates.date2num(timestamps)
print('first timestamp: '+str(timestamps[0])+'  ('+str(timestamps_num[0])+')')
print('last timestamp:  '+str(timestamps[-1])+'  ('+str(timestamps_num[-1])+')')
fit=numpy.polyfit(timestamps_num, numpy.log(datamax)/numpy.log(logbase), 1)
#fit=numpy.polyfit(timestamps_num, datamax, 1)
print('fit: '+str(fit))
print(numpy.log(logbase))
ax.plot(timestamps, numpy.log(datamax)/numpy.log(logbase))
ax.plot(timestamps, numpy.log(dataavg)/numpy.log(logbase))
ax.plot(timestamps, numpy.log(datamin)/numpy.log(logbase))
ax.plot(timestamps_num, fit[1]+fit[0]*timestamps_num)
#ax.plot(timestamps, datamax)
#ax.plot(timestamps, dataavg)
#ax.plot(timestamps, datamin)

plt.grid()
plt.savefig('results/results.png')
plt.show()

