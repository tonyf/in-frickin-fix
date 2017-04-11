import numpy as np
import scipy.spatial as sp
import collections
import math
from q_classifier import QClassifier

from document_classifier.classifier import DocClassifier

Sentence = collections.namedtuple('Sentence', 'text matrix')
Doc = collections.namedtuple('Doc', 'title text matrix category')
EMBEDDING_SIZE = 300


class Answerer(object):
    # def __init__(self, docs, nlp):
    #     self.nlp = nlp
    #     self.docs = parse_docs(docs)

    def __init__(self, set_dict, nlp):
        self.nlp = nlp
        self.docs = parse_docs(docs)

    def get_category_docs(self, category):
        return [d for d in self.docs if d.category == category]

    def find_probable_doc(self, q):
        TOPIC_SIZE = 200
        max_sim = float("-inf")
        best_doc = None
        for key in self.set_dict:
            for doc in self.set_dict[key]:
                # If the question mentions a named entity
                topic = doc
                sim = topic.similarity(q)
                if sim > max_sim:
                    max_sim = sim
                    best_doc = doc
        print best_doc[0:25]
        return best_doc

    def find_answer_doc(self, question):
        q = self.nlp(question)
        entity = None
        if q.ents:
            entity = q.ents[0]
        else:
            # No named entities, search with biggest vector
        category = ent2category(entity)
        category_docs = self.get_category_docs(category)
        # Cosine similarity?
        return None

    def find_answer_sentence(self, q, doc, window):
        matrix = get_doc_matrix(doc)
        smallest = matrix[0]
        s_dist = compute_dist(matrix[0].matrix, q)
        s_index = 0

        for i in range(len(matrix)):
            s = matrix[i]
        stop = s_index+step+1 if s_index+step < len(doc_matrix) else len(doc_matrix)
        return doc_matrix[start:stop]

    def get_answer(self, question, window):
        q = self.nlp(question)
        qclassifier = QClassifier(q)
        qtype = qclassifier.type
        doc = self.find_probable_doc(q)
        # d = self.get_answer_doc(q)
        m = get_sentence_matrix(q)
        answer = self.find_answer_sentence(m, doc, window)
        text = [x.text.strip() for x in answer]
        return ' '.join(text)

def parse_docs(docs):
    docs = []
    classifier = DocClassifier()
    for doc in docs
        d = Doc(title=get_doc_title(doc), text=doc, matrix=get_doc_matrix(doc), category=classifier.predict(doc))
        docs.append(d)
    return docs

def get_doc_title(doc):
    return ""

def get_doc_matrix(doc):
    sentences = []
    for sent in doc.sents:
        s = Sentence(text=sent.text, matrix=get_sentence_matrix(sent))
        sentences.append(s)
    return sentences

def get_sentence_matrix(s):
    n = len(s)
    matrix = np.zeros((EMBEDDING_SIZE, 1))
    matrix[:,0] = s.vector
    return matrix
