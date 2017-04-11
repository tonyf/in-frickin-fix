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

# A class that takes a question and classifies it
class QClassifier:
    def __init__(self, question):
        self.question = question
        self.qtext = question.text
        self.type = self.classify()
    
    def classify(self):
        split_sent = re.findall(r'[\w]+', self.qtext)
        split_sent = [x.lower() for x in split_sent]
        N = len(split_sent)
        
        # Check for leading auxiliary verb => YESNO
        sent = self.question.sents.next()
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
    qclass = QClassifier(q.sents.next())
