import os
import sys
from Process import Process
from Summary import Summary

# Log File Parameters
inpath = sys.argv[1]
outpath = './output/'

# Log Parser Parameters
isfromjson = False
is_walks = True
is_generatevector = True
detection = sys.argv[2]

#Community Detection Parameters
meth = 'HRW'
issplit = False
vector_or_lda = 'vector' #{vector, lda}
number_walks = 100 #Net2:600
walk_length = 200 #Net2:120
window_size = 20  #this parameter is only for 'vector', Net2:30
embedding_size = 20  #this parameter is only for 'vector' Net1:5, Net2:5, Net3:5
sg = 1  #skip-gram {1}; CBOW {0}. This parameter is only for 'vector'
hs = 0  #hierarchical softmax {1}; negative sampling {0}. This parameter is only for 'vector'
epoch = 300 #Net2:100
batch = 1000 #Net2:20

process = Process(inpath, detection, outpath)
process.run(
		isfromjson = isfromjson,
		is_walks = is_walks,
		is_generatevector = is_generatevector,
		meth = meth,
		vector_or_lda = vector_or_lda,
		number_walks = number_walks,
		walk_length = walk_length,
		window_size = window_size,
		embedding_size = embedding_size,
		sg = sg,
		hs = hs,
		epoch = epoch,
		batch = batch)

filename = inpath.split('/')[-1]
filename = filename.split('.')[0]
summary = Summary(filename, detection)
summary.run()


