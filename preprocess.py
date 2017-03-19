"""
This code tokenizes the input data into sentences using nltk, then feeds each
sentence to the Berkeley Parser.
OUTPUT:
sentence
parsed sentence

"""

import os
import sys
from BerkeleyParser import *
from nltk.corpus import treebank
import nltk
import codecs
from nltk.tokenize import sent_tokenize, word_tokenize

root_dir = sys.argv[1]
files = []
set1 = "set1"
set2 = "set2"
set3 = "set3"
set4 = "set4"

#Open the subfolder set1 and read all the .txt files in it
path1 = os.path.join(root_dir,set1)
for i in os.listdir(path1):
    if i.endswith('.txt'):
	files.append(codecs.open(os.path.join(path1,i),'r'))

i = 0
for f in files:
	lines = []
	text = f.read()
	text = text.decode('utf-8')
    	sents = sent_tokenize(text)
	break


for line in sents:
	print line
	b_parse(line)
