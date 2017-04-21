import codecs
import re
import os
import spacy
import sys
from operator import itemgetter

# Open the directory given by the arguments and read all the .txt files in it
def read_doc(filename):
    topic = None
    temp = []
    with codecs.open(filename, 'r') as f:
        topic = ""
        line = f.readline()
        while line != "":
            stripped = line.strip()
            if len(stripped) > 0 and stripped[-1] in ['.', ';', '?', '!']:
                dash_replaced = re.sub(r'\xe2\x80\x93', '-', stripped)
                temp.append(unicode(dash_replaced, encoding='ascii', errors='ignore'))
            line = f.readline()
    text = " ".join(temp)
    return (topic, text)

def read_questions(filename):
    questions = []
    with open(filename) as f:
        for line in f:
            q = unicode(line.strip(), encoding='ascii', errors='ignore')
            questions.append(q)
    return questions

def read_in_set(root_dir, set_name):
    texts = []
    files = []
    topics = []
    fpath = os.path.join(root_dir, set_name)
    for i in os.listdir(fpath):
        if i.endswith('.txt'):
            files.append(os.path.join(fpath, i))

    for filename in files:
        topic, text = read_doc(filename)
        topics.append(topic)
        texts.append(text)

    return texts, files, topics

# Resolve pronoun co-references within a label (NER class)
def resolve_coreferences(doc, pronoun_list, label, is_possessive):
    new_text = []
    p_last = (0, 0)
    for p in pronoun_list:
        if doc.text[p[1]-1] == '.':
            p = (p[0], p[1] - 1)

        candidates = [(e.text, e.start_char) for e in doc.ents
                      if e.label_ == label and e.start_char < p[0]]
        if len(candidates) > 0:
            replacement = max(candidates, key = itemgetter(1))[0]
            position = max(candidates, key = itemgetter(1))[1]
            replacement = replacement + "'s" if is_possessive else replacement
        else:
            replacement = doc.text[p[0]:p[1]]
            position = p[0]
        # Check if the resolved co-reference is in the same sentence
        same_sent = True
        for i in range(position, p[0] + 1):
            if doc.text[i-1] in [".", "?", "!"] and doc.text[i] == " ":
                same_sent = False
        if same_sent:
            continue
        new_text.append(doc.text[p_last[1]:p[0]] + " " + replacement + " ")
        p_last = p
    new_text.append(doc.text[p_last[1]:])
    return "".join(new_text)

def preprocess(txt, nlp):
    # Put spaces before and after hyphens (for spacy)
    new_txt = re.sub(r'-', ' - ', txt)
    new_txt = re.sub(r'  -  ', ' - ', new_txt)

    # Perform NLP on each file's contents
    #TODO: possibly throw away or handle separately section headers (lines without any periods)
    doc = nlp(new_txt)
    #TODO: insert topic here?

    # Co-reference resolution
    per_re = r'( He )|( he )|( Him )|( him )|( She )|( she )|( him\.)|( he\.)|( she\.)'
    per_list = [(m.start(), m.end()) for m in re.finditer(per_re, doc.text)]
    new_txt = resolve_coreferences(doc, per_list, "PERSON", False)

    pos_re = r'( His )|( his )|( Hers )|( hers )|( his\.)|( hers\.)'
    pos_list = [(m.start(), m.end()) for m in re.finditer(pos_re, new_txt)]
    doc = nlp(new_txt)
    new_txt = resolve_coreferences(doc, pos_list, "PERSON", True)

    loc_re = r'( There )|( there )'
    loc_list = [(m.start(), m.end()) for m in re.finditer(loc_re, new_txt)]
    #TODO: location-based co-ref resolution

    doc = nlp(new_txt)
    her_list = []
    for i in range(len(doc)):
        if doc[i].string in [u"Her ", u"her ", u"her"] and doc[i].tag_ == "PRP$":
            her_list.append((doc[i].idx, doc[i+1].idx))
    new_txt = resolve_coreferences(doc, her_list, "PERSON", True)

    doc = nlp(new_txt)
    return doc


# Pre-process all sets
def preprocess_docs(root_dir, set_list, nlp):
    docs = []
    for s in set_list:
        texts, files, topics = read_in_set(root_dir, s)
        num_files = len(files)

        for i in range(num_files):
            filename = files[i]
            txt = texts[i]
            docs.append(preprocess(txt, nlp))

    return docs


# Testbed for pre-processing
if __name__ == "__main__":
    root_dir = sys.argv[1]
    #sets = ["set1", "set2", "set3", "set4"]
    sets = ["test_set"]
    nlp = spacy.load("en")
    set_dict = preprocess_docs(root_dir, sets, nlp)
    print set_dict["set1"][0]
