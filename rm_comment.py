#!/usr/bin/env python
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-

import os
import sys
import re

reload(sys)

sys.setdefaultencoding('utf8')

folder = "/Users/penghuailiang/Documents/projects/huailiang.github.io/source/js/jax/output/HTML-CSS/fonts"


def format_file(file):
	lines = []
	with open(file, 'r') as f:
		lines = f.readlines()
		for i in range(len(lines)):
			if "//" in lines[i]:
				line = lines[i]
				print(line)
				idx = line.rfind("//")
				if idx > 0 :
					lines[i] = line[:idx]+"\n"
					print(line)
	with open(file, 'w') as f:
		f.writelines(lines)

def rm_all_invalid(folder):
	for d in os.listdir(folder):
		file =  os.path.join(folder,d)
		if os.path.isdir(file):
			rm_all_invalid(file)
		elif os.path.isfile(file):
			print(file)
			format_file(file)

if __name__=='__main__':
	rm_all_invalid(folder)
