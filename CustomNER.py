# NerHandler performs Named Entity Recognition (NER) on all data in a set

import codecs
import os
import spacy
import sys

# Open the directory given by the arguments and read all the .txt files in it
def read_in_set(root_dir, set_name):
    texts = []
    files = []
    topics = []
    fpath = os.path.join(root_dir, set_name)
    for i in os.listdir(fpath):
        if i.endswith('.txt'):
            files.append(os.path.join(fpath, i))

    for filename in files:
        with codecs.open(filename, 'r') as f:
            topic = f.readline()
            topics.append(topic)
            txt = f.read()
            txt = unicode(txt, encoding = 'ascii', errors = 'ignore')
            texts.append(txt)

    return texts, files, topics

# Read in the data from a given set
root_dir = sys.argv[1]
set1 = "set1"
texts, files, topics = read_in_set(root_dir, set1)

# Initialize the spacy natural language processor
nlp = spacy.load('en')
nlp.entity.add_label("TOPIC")

# Create a dict with Key = doc and Value = a set of named entities in the doc
fdict = {}
for i in range(len(files)):
    filename = files[i]
    txt = texts[i]
    fdict[filename] = set()
    # Perform NLP on each file's contents     
    #TODO: possibly throw away or handle separately section headers (lines without any periods)    
    doc = nlp(txt)
    #TODO: insert topic here
    for ent in doc.ents:
        fdict[filename].add((ent.label_, ent.text))

#TODO: tag first line of document as a TOPIC Named Entity type and draw inferences from that
# if later the same entity has another tag, defer to that.
# This will likely require a pipeline update that allows for TOPIC to be included as a type.
