import codecs
import re
import os
import spacy
import sys
from operator import itemgetter

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

# Resolve pronoun co-references within a label (NER class)
def resolve_coreferences(doc, pronoun_list, label, is_possessive):
    new_text = []
    p_last = (0, 0)
    for p in pronoun_list:
        candidates = [(e.text, e.start) for e in doc.ents 
                      if e.label_ == label and e.start < p[0]]
        replacement = max(candidates, key = itemgetter(1))[0]
        replacement = replacement + "'s" if is_possessive else replacement
        new_text.append(doc.text[p_last[1]:p[0]] + " " + replacement + " ")
        p_last = p
    new_text.append(doc.text[p_last[1]:])
    return "".join(new_text)

# Pre-process all sets
def preprocess_docs(root_dir):
    # Initialize the spacy natural language processor
    nlp = spacy.load('en')
    
    sets = ["set1", "set2", "set3", "set4"]
    set_dict = {}
    for s in sets:
        texts, files, topics = read_in_set(root_dir, s)
        num_files = len(files)
        
        set_dict[s] = []
        
        for i in range(num_files):
            filename = files[i]
            txt = texts[i]
            # Perform NLP on each file's contents     
            #TODO: possibly throw away or handle separately section headers (lines without any periods)    
            doc = nlp(txt)
            #TODO: insert topic here
                
            # Co-reference resolution
            per_re = r'( He )|( he )|( Him )|( him )|( She )|( she )|( Her )|( her )'
            per_list = [(m.start(), m.end()) for m in re.finditer(per_re, txt)]
            txt = resolve_coreferences(doc, per_list, "PERSON", False)
                
            per_pos_re = r'( His )|( his )|( Her )|( her )|( Hers )|( hers )'
            per_pos_list = [(m.start(), m.end()) for m in re.finditer(per_pos_re, txt)]
            txt = resolve_coreferences(doc, per_pos_list, "PERSON", True)
            
            #TODO: there may be a better way to modify the doc than to remake it
            doc = nlp(txt)
            set_dict[s].append(doc)
        
    return set_dict

# Testbed for pre-processing
if __name__ == "__main__":
    root_dir = sys.argv[1]
    set_dict = preprocess_docs(root_dir)
    print set_dict["set1"][0]
