import re
import spacy

# An enumeration for types of questions
class QType:
    WHO = 0
    WHAT = 1
    WHERE = 2
    WHEN = 3
    WHY = 4
    HOW = 5
    COUNT = 6
    YESNO = 7
    UNKNOWN = 8

# spaCy NERs:

# PERSON	   People, including fictional.
# NORP	       Nationalities or religious or political groups.
# FACILITY	   Buildings, airports, highways, bridges, etc.
# ORG	       Companies, agencies, institutions, etc.
# GPE      	   Countries, cities, states.
# LOC	       Non-GPE locations, mountain ranges, bodies of water.
# PRODUCT	   Objects, vehicles, foods, etc. (Not services.)
# EVENT	       Named hurricanes, battles, wars, sports events, etc.
# WORK_OF_ART  Titles of books, songs, etc.
# LANGUAGE	   Any named language

# DATE	       Absolute or relative dates or periods.
# TIME	       Times smaller than a day.
# PERCENT	   Percentage, including "%".
# MONEY	       Monetary values, including unit.
# QUANTITY	   Measurements, as of weight or distance.
# ORDINAL	   "first", "second", etc.
# CARDINAL	   Numerals that do not fall under another type.

def has_type(sent, qtype):
    # Unhandled types
    if qtype not in [QType.WHO, QType.WHEN, QType.COUNT]:
        return True
    for i in range(len(sent)):
        if qtype == QType.WHO and sent[i].ent_type_ == "PERSON":
            return True
        elif qtype == QType.WHEN and sent[i].ent_type_ == "DATE":
            return True
        elif qtype == QType.COUNT and sent[i].ent_type_ == "QUANTITY":
            return True
    return False

def get_template(sent, qtype):
    if not has_type(sent, qtype):
        return None
    
    ent_idx = None
    mv_idx = None
    template = None
    for i in range(len(sent)):
        # set the template
        if qtype == QType.WHO and sent[i].ent_type_ == "PERSON":
            template = "{0} is the person who {1}"
            ent_idx = i
        elif qtype == QType.WHEN and sent[i].ent_type_ == "DATE":
            template = None
        elif qtype == QType.COUNT and sent[i].ent_type_ == "QUANTITY":
            template = None
        
        # find the main verb
        if sent[i].text == sent.root.text:
            mv_idx = i
    
    # return the whole sentence if we fail to find the needed info.
    if ent_idx is None or mv_idx is None or template is None:
        return sent.text
    
    answer = template.format(sent[ent_idx], sent[mv_idx:])    
    return answer

def qclassify(question):
    qtext = question.text
    split_sent = re.findall(r'[\w]+', qtext)
    split_sent = [x.lower() for x in split_sent]
    N = len(split_sent)

    # Check for leading auxiliary verb => YESNO
    sent = question.sents.next()
    mv = sent.root
    for child in mv.children:
        if child.dep_ == "aux" and child.idx == 0:
            # if an auxiliary verb is at the start of the sentence
            return QType.YESNO

    # Check for interrogative words
    for i in range(N):
        word = split_sent[i]
        if word in ["who", "whom"]:
            return QType.WHO
        elif word == "what":
            return QType.WHAT
        elif word == "where":
            return QType.WHERE
        elif word == "when":
            return QType.WHEN
        elif word == "why":
            return QType.WHY
        elif word == "how":
            if i < N - 1 and split_sent[i+1] in ["much", "many"]:
                return QType.COUNT
            else:
                return QType.HOW

    # Failed to classify the question
    return QType.UNKNOWN

# Test bed
if __name__ == "__main__":
    nlp = spacy.load("en")
    #question = u"What hath God wrought?"
    question = u"Does he go to market?"
    q = nlp(question)
    qclass = qclassify(q.sents.next())
