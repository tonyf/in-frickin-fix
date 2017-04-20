import re
import spacy
from lib.antonyms import *
import doc_utils as du


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

# PERSON       People, including fictional.
# NORP         Nationalities or religious or political groups.
# FACILITY     Buildings, airports, highways, bridges, etc.
# ORG          Companies, agencies, institutions, etc.
# GPE          Countries, cities, states.
# LOC          Non-GPE locations, mountain ranges, bodies of water.
# PRODUCT      Objects, vehicles, foods, etc. (Not services.)
# EVENT        Named hurricanes, battles, wars, sports events, etc.
# WORK_OF_ART  Titles of books, songs, etc.
# LANGUAGE     Any named language

# DATE         Absolute or relative dates or periods.
# TIME         Times smaller than a day.
# PERCENT      Percentage, including "%".
# MONEY        Monetary values, including unit.
# QUANTITY     Measurements, as of weight or distance.
# ORDINAL      "first", "second", etc.
# CARDINAL     Numerals that do not fall under another type.

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

def evaluate_yn(sent, q, qtype):
    if qtype != QType.YESNO:
        return None
    
    # Evaluate negation in both sentences 
    quest = q.sents.next()
    qmv = quest.root
    quest_neg = False
    for child in qmv.children:
        if child.dep_ == "neg":
            quest_neg = True
    smv = sent.root
    sent_neg = False
    for child in smv.children:
        if child.dep_ == "neg":
            sent_neg = True
    negated = True if quest_neg != sent_neg else False
    
    # Find the key words in the question and the answering sentence
    word_pairs = []
    for i in range(len(sent)):
        for j in range(len(quest)):
            sim = sent[i].similarity(quest[j])
            word_pairs.append((i, j, sim))
    sorted_pairs = sorted(word_pairs, key=lambda x: x[2], reverse=True)
    ur_word_s = [sent[sorted_pairs[0][0]], sent[sorted_pairs[1][0]]]
    ur_word_q = [quest[sorted_pairs[0][1]], quest[sorted_pairs[1][1]]]
    
    # Evaluate similarity of key words
    comparison = True
    for i in range(len(ur_word_s)):
        if ur_word_s[i].lemma_ != ur_word_q[i].lemma_:
            comparison = False

    # Check that quantitative Named Entities in the quest match the sent
    sent_ents = du.get_ents_in_sent(sent)
    sent_ents = [x.text for x in sent_ents]
    named_entities_match = True
    for qent in q.ents:
        if qent.label_ in [u"DATE", u"TIME", u"PERCENT", u"MONEY",
                u"QUANTITY", u"ORDINAL", u"CARDINAL"]:
            if qent.text not in sent_ents:
                named_entities_match = False
    
    # Check for reversed comparatives and superlatives
    sups_dict = get_superlatives()
    comps_dict = get_comparatives()
    adjs_match = True
    for i in range(len(sent)):
        sword = sent[i].text.strip().lower()
        is_sup = sword in sups_dict.keys()
        is_cmp = sword in comps_dict.keys()
        if not is_sup and not is_cmp:
            continue
        qwords = quest.text.lower().split()
        if sword in qwords:
            adjs_match = True
            break
        elif is_sup and sups_dict[sword] in qwords:
            adjs_match = False
            break
        elif is_cmp and comps_dict[sword] in qwords:
            adjs_match = False
            break

    if comparison != negated and adjs_match and named_entities_match:
        # Answer is True
        return True
    else:
        # Answer is False
        return False

def get_template(sent, quest, qtype):
    if not has_type(sent, qtype):
        return None
    
    # Evaluate YESNO questions
    if qtype == QType.YESNO:
        ans_val = evaluate_yn(sent, quest, qtype)
        ans = "Yes" if ans_val else "No"
        s = sent.text
        s = s[0].lower() + s[1:] if sent[0].ent_type_ == "" else s
        template = "{0}, {1}".format(ans, s)
        return template
    
    # Evaluate other supported question types
    ent_idx = None
    mv_idx = None
    template = None
    for i in range(len(sent)):
        # set the template
        if qtype == QType.WHO and sent[i].ent_type_ == "PERSON":
            #template = "{0} is the person who {1}"
            #ent_idx = i
            template = None
        elif qtype == QType.WHEN and sent[i].ent_type_ == "DATE":
            template = None
        elif qtype == QType.COUNT and sent[i].ent_type_ == "QUANTITY":
            template = None
        
        # find the main verb
        if sent[i].text == sent.root.text:
            mv_idx = i
    
    # Return the whole sentence if we fail to find the needed info.
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
    if mv.lemma_ == "be" and mv.idx == 0:
        # if the main verb is a form of "to be" and is at the start
        return QType.YESNO
        
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
