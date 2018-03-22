from pathlib import Path
import os, glob
from multiprocessing import Pool
from subprocess import call
from config import source_path, destination_path

file_list = []
os.chdir(source_path)



for file in glob.glob("*.mp4"):
	file_list.append(source_path+file)


def compression(filename):
	file1 = filename.rsplit('/', 1)
	print(destination_path+file1[1])
	if os.path.exists(destination_path+file1[1]):
		print("File Already compressed::", filename)
	else:	
		string = "ffmpeg -i "+ filename +" -crf 32 "+destination_path+file1[1]
		print(string)	
		os.system(string)



p = Pool(4)

try:
	arrLevel = []
	arrLevel = p.map(compression, file_list)
	p.close()
	p.join()
	
except Exception as e:
	print(e)
