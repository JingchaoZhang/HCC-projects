#!/util/opt/anaconda/4.3/envs/python-2.7/bin/python

import csv
import pylab
import matplotlib.patches as mpatches

DedicGroups = [	'starace',
		'abg',
		'bigweather',
		'esquared',
		'tsymbal',
		'ahouston',
		'alexandrov',
		'stats',
		'statsgeneral',
		'francisco',
		'jclarke',
		'zeng',
		'waterforfood',
		'juancui',
		'choueiry',
		'benson',
		'guda',
		'larios',
		'riethoven']
xShare = []
yShare = []
xDedic = []
yDedic = []

with open("query.txt", "rb") as f:
    reader=csv.reader(f, delimiter=' ')
    for row in reader:
	if all(i not in row for i in DedicGroups):
	    xShare.append(row[2])
	    yShare.append(row[3])
	else:
	    xDedic.append(row[2])
	    yDedic.append(row[3])

pylab.xlabel('Requested CPU Hours')
pylab.ylabel('Job Queue Time (h)')
pylab.plot(xShare, yShare, 'ro', xDedic, yDedic, 'g^')
red_patch = mpatches.Patch(color='red', label='Shared')
green_patch = mpatches.Patch(color='green', label='Dedicated')
pylab.legend(handles=[red_patch, green_patch])

pylab.show()
