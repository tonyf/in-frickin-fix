import spacy
import os
import sys
import re
from preprocess import preprocess_docs

root_dir = "data/"
setlist = ["set1","set2","set3","set4"]
nlp = spacy.load("en")

#Call the spacy preprocess module
def preprocess(setlist, nlp):
	set_dict = preprocess_docs(root_dir,setlist,nlp)
	return set_dict

def superlatives(set_dict):
	sups = set([])
	for doc in set_dict:
		sents = doc.sents
		for s in sents:
			mv = s.root
			for word in mv.subtree:
				if word.tag_ == "JJS":
					sups.add(word.string.strip().lower())
	return sups

def get_superlatives():
	f = open("lib/superlatives.txt", "r")
	sups_dict = {}
	line = f.readline()
	while line != "":
		sups = line.split(",")
		sups_dict[sups[0]] = sups[1]
		line = f.readline()
	print sups_dict

def main():
	# set_dict = preprocess(setlist,nlp)
	# sups = superlatives(set_dict)
	# f = open("superlatives.txt", "w")
	# for word in sups:
	# 	f.write(word+"\n")

	# f.close()
	print "starting..."
	f = open("lib/superlatives.txt", "r")
	sups_dict = {}
	line = f.readline()
	while line != "":
		print line
		sups = line.split(",")
		sups_dict[sups[0]] = sups[1].strip()
		line = f.readline()
	print sups_dict

main()