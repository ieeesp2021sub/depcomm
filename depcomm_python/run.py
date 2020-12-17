import argparse
import os

def parse_args():

	parser = argparse.ArgumentParser(description="Run depcomm.")
	
	parser.add_argument('--logpath',nargs='?',default='./input/leak_data.txt')
	parser.add_argument('--poi',nargs='?',default='10.10.103.10:38772-\>159.226.251.11:25')

	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()

	inputfile = args.logpath #log
	detection = args.poi #POI
	if '>' in detection:
		detection = detection.replace('>','\>')

	os.system('python2 core/Start.py '+inputfile+' '+detection)
