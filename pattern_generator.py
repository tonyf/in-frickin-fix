import os
import sys
import re
import nltk
import codecs
from nltk.tokenize import sent_tokenize, word_tokenize

def generate_questions():
    root_dir = sys.argv[1]
    files = []
    set1 = "set1"
    set2 = "set2"
    set3 = "set3"
    set4 = "set4"

    #Open the subfolder set1 and read all the .txt files in it
    # TODO: do this for the other sets
    path1 = os.path.join(root_dir,set1)
    for i in os.listdir(path1):
        if i.endswith('.txt'):
            files.append(codecs.open(os.path.join(path1,i),'r'))

    for f in files:
        text = f.read()
        text = text.decode('utf-8')
        sents = sent_tokenize(text)
        break

    for line in sents:
        print line

def generate_patterns():
    pass

def read_patterns():
    f = open("patterns.txt", 'r')
    pass

def main():
    generate_questions()

if __name__ == "__main__":
    main()
