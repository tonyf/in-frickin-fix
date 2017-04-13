# NerHandler performs Named Entity Recognition (NER) on all data in a set

import codecs
import nltk
import os
import re
import sys

# Open the directory given by the arguments and read all the .txt files in it
def read_in_set(root_dir, set_name):
    docs = []
    files = []
    fpath = os.path.join(root_dir,set1)
    for i in os.listdir(fpath):
        if i.endswith('.txt'):
            files.append(os.path.join(fpath, i))

    for filename in files:
        with codecs.open(filename, 'r') as f:
            # Keep lines separate to avoid confusing the parser with section headers;
            # all sentences are contained on one line.
            doc = f.readlines()
            doc = [unicode(line, encoding = 'ascii', errors = 'ignore') for line in doc]
            docs.append(doc)

    return docs, files

# Read in the data from a given set
root_dir = sys.argv[1]
set1 = "set1"
docs, files = read_in_set(root_dir, set1)

# Create a dict with Key = doc and Value = a set of named entities in the doc
fdict = {}
for i in range(len(files)):
    filename = files[i]
    doc = docs[i]
    fdict[filename] = set()
    # Tokenize the text into sentences, then words
    for line in doc:
        
        #TODO: possibly throw away or handle separately section headers (lines without any periods)
        
        text_sents = nltk.sent_tokenize(line)
        for sent in text_sents:
            text_tokens = nltk.word_tokenize(sent)
            # Insert part-of-speech tags
            tagged = nltk.pos_tag(text_tokens)
            # Generate Named Entities as a tuple (Label, Value)
            parse_tree = nltk.ne_chunk(tagged, binary=False)
            named_entities = [x for x in parse_tree if type(x) == nltk.tree.Tree]
            named_entities = [(x.label(), " ".join([y[0] for y in x.leaves()])) for x in named_entities]
            fdict[filename].update(named_entities)

# Extract relationships
IN = re.compile(r'.*\bin\b(?!\b.+ing)')
print nltk.sem.extract_rels('PERSON', 'ORGANIZATION', parse_tree, pattern = IN)
