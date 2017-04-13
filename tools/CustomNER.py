# NerHandler performs Named Entity Recognition (NER) on all data in a set

import codecs
import re
import os
import spacy
import sys
from operator import itemgetter
'''
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
'''
def resolve_coreferences(entity_list, text, pronoun_list, label, is_possessive):
    new_text = text
    for p in pronoun_list:
        candidates = [(e.text, e.start) for e in entity_list 
                      if e.label_ == label and e.start < p[0]]
        replacement = max(candidates, key = itemgetter(1))[0]
        replacement = replacement + "'s" if is_possessive else replacement
        new_text = new_text[:p[0]] + " " + replacement + " " + new_text[p[1]:]
    return new_text
'''
# Read in the data from a given set
root_dir = sys.argv[1]
set1 = "set1"
texts, files, topics = read_in_set(root_dir, set1)
num_files = len(files)
'''

texts = [unicode("There is a house in New Orleans they call the rising sun.", encoding = 'ascii', errors = 'ignore')]
files = ["testfile"]
num_files = len(files)

# Initialize the spacy natural language processor
nlp = spacy.load('en')
nlp.entity.add_label("TOPIC")

# Create a dict with Key = doc and Value = a set of named entities in the doc
fdict = {}
for i in range(num_files):
    filename = files[i]
    txt = texts[i]
    fdict[filename] = []
    # Perform NLP on each file's contents     
    #TODO: possibly throw away or handle separately section headers (lines without any periods)    
    doc = nlp(txt)
    #TODO: insert topic here
    for ent in doc.ents:
        fdict[filename].append(ent)
        
    # Co-reference resolution
    per_re = r'( He )|( he )|( Him )|( him )|( She )|( she )|( Her )|( her )'
    per_list = [(m.start(), m.end()) for m in re.finditer(per_re, txt)]
    texts[i] = resolve_coreferences(doc.ents, txt, per_list, "PERSON", False)
        
    per_pos_re = r'( His )|( his )|( Hers )|( hers )'
    per_pos_list = [(m.start(), m.end()) for m in re.finditer(per_pos_re, txt)]
    texts[i] = resolve_coreferences(doc.ents, txt, per_pos_list, "PERSON", True)
    

#TODO: tag first line of document as a TOPIC Named Entity type and draw inferences from that
# if later the same entity has another tag, defer to that.
# This will likely require a pipeline update that allows for TOPIC to be included as a type.
