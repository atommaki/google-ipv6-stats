#!/usr/bin/python3


import urllib.request, urllib.error, urllib.parse
import re
import datetime
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import csv

response = urllib.request.urlopen('https://www.google.com/intl/en_ALL/ipv6/statistics/data/adoption.js')

datalineregex=re.compile('^ *\[20.., .*\],$')
timestamps = []
data = []
datamin = []
dataavg = []
datamax = []
statdf = pd.DataFrame( columns = [ 'year', 'day', 'avg', 'min', 'max', 'norm_avg', 'norm_min', 'norm_max' ] )

last7 = [ 0, 0, 0, 0, 0, 0 ,0]
i = 0
n = 0
jan1 = {}
with open('results/results.csv', 'w') as f:
    wr = csv.writer(f)
    for line in response.read().splitlines():
        if datalineregex.match(line.decode("utf-8")):
            trans = dict.fromkeys(map(ord, '[] '), None) # to remove '[', ']', ' '
            datalist = line.decode("utf-8").translate(trans).split(',')
            wr.writerow(datalist)
            current_timestamp = datetime.datetime(year=int(datalist[0]),month=int(datalist[1])+1,day=int(datalist[2]))
            timestamps = timestamps+[ current_timestamp ]
            last7[i]=float(datalist[3])
            if i == 6:
                i=0
            else:
                i=i+1
            #data=data+[ float(datalist[3]) ]
            datamin=datamin+[ min(last7) ]
            dataavg=dataavg+[ sum(last7)/7 ]
            datamax=datamax+[ max(last7) ]
            if current_timestamp.timetuple().tm_yday == 1:
                # this is 1st January!
                jan1[current_timestamp.year] = {
                                                'avg': sum(last7)/7,
                                                'min': min(last7),
                                                'max': max(last7)
                                               }
            if current_timestamp.year in jan1.keys():
                norm_avg = sum(last7)/7 - jan1[current_timestamp.year]['avg']
                norm_min = min(last7)   - jan1[current_timestamp.year]['min']
                norm_max = max(last7)   - jan1[current_timestamp.year]['max']
            else:
                norm_avg = None
                norm_min = None
                norm_max = None
            statdf.loc[n] = [ int(current_timestamp.year), #year
                              int(current_timestamp.timetuple().tm_yday), # day of the year
                              sum(last7)/7, # avg
                              min(last7),   # min
                              max(last7),   # max
                              norm_avg,
                              norm_min,
                              norm_max
                            ]
            #statdf.loc[n] = [ int(current_timestamp.year), int(current_timestamp.strftime('%j')), sum(last7)/7 ]
            n += 1

fig, ax = plt.subplots()
ax.set_ylabel('log')
#ax2 = ax.twinx()

logbase=2
timestamps_num=mdates.date2num(timestamps)
print('first timestamp: '+str(timestamps[0])+'  ('+str(timestamps_num[0])+')')
print('last timestamp:  '+str(timestamps[-1])+'  ('+str(timestamps_num[-1])+')')
fit=numpy.polyfit(timestamps_num, numpy.log(datamax)/numpy.log(logbase), 1)
#fit=numpy.polyfit(timestamps_num, datamax, 1)
print('fit: '+str(fit))
print(numpy.log(logbase))
#ax.plot(timestamps, numpy.log(datamax)/numpy.log(logbase))
ax.plot(timestamps, numpy.log(dataavg)/numpy.log(logbase))
#ax.plot(timestamps, numpy.log(datamin)/numpy.log(logbase))
ax.plot(timestamps_num, fit[1]+fit[0]*timestamps_num)
#ax.plot(timestamps, datamax)
#ax.plot(timestamps, dataavg)
#ax.plot(timestamps, datamin)

plt.grid()
plt.savefig('results/results.png')
plt.show()

#fig2, ax2 = plt.subplots()
ax3 = plt.gca()
# for year in range(2009, 2019):
#     print(f" ------------------- { year } --------------------- ")
#     print(statdf.loc[statdf['year'] == year ])
# #    ax2.plot(x = statdf.loc[statdf['year'] == year ]['day'],
# #             y = statdf.loc[statdf['year'] == year ]['percent'])
#     statdf.loc[statdf['year'] == year ].plot(x = 'day', y = 'percent', ax = ax3)

c = { '2013': 'red',
      '2014': 'blue',
      '2015': 'yellow',
      '2016': 'purple',
      '2017': 'green',
      '2018': 'brown',
      '2019': 'pink',
      '2020': 'orange',
      '2021': 'black',
    }
print(statdf)

#statdf.loc[statdf['year'] > 2012 ].groupby('year').plot(x = 'day', y = 'norm_min', legend = False, ax = ax3)
#statdf.loc[statdf['year'] > 2012 ].groupby('year').plot(x = 'day', y = 'norm_avg', legend = False, ax = ax3)
statdf.loc[statdf['year'] > 2012 ].groupby('year').plot(x = 'day', y = 'norm_max', legend = False, ax = ax3)
plt.title('IPv6 usage')
plt.ylabel('%')
plt.xlabel('Day of the year')
current_handles, _ = plt.gca().get_legend_handles_labels()
reversed_handles = reversed(current_handles)
labels = reversed(statdf['year'].unique())
plt.legend(reversed_handles,labels,loc='lower right')
plt.grid()
plt.show()

