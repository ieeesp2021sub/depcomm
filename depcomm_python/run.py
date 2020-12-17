import os

inputlog = 'leak_data.txt' #log file name
POI = '10.10.103.10:38772\-\>159.226.251.11:25' #POI

os.system('python2 core/Start.py '+inputlog+' '+POI)
