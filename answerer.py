import numpy as np
import scipy.spatial as sp
import collections
import math

from document_classifier.classifier import DocClassifier

Sentence = collections.namedtuple('Sentence', 'text matrix')
Doc = collections.namedtuple('Doc', 'title text matrix category')
EMBEDDING_SIZE = 300


class Answerer(object):
    def __init__(self, docs, nlp):
        self.nlp = nlp
        self.docs = parse_docs(docs)

    def get_category_docs(self, category):
        return [d for d in docs if d.category == category]


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



        # TODO: Find NERs. Match NER to class. Search wihthin class
        return None

    def find_answer_sentence(self, doc_matrix, question_matrix, window):
        smallest = doc_matrix[0]
        s_dist = compute_dist(doc_matrix[0].matrix, q)
        s_index = 0

        for i in range(len(doc_matrix)):
            s = doc_matrix[i]
            dist = compute_dist(s.matrix, q)
            if dist < s_dist:
                smallest = s
                s_dist = dist
                s_index = i
        step = int(math.floor(float(window) / 2))
        start = s_index-step if s_index-step > 0 else 0
        stop = s_index+step+1 if s_index+step < len(doc_matrix) else len(doc_matrix)
        return doc_matrix[start:stop]

    def get_answer(self, question, window):
        q = self.nlp(question)
        d = self.get_answer_doc(q)
        m = get_sentence_matrix(q)
        answer = self.find_answer_sentence(d.matrix, m, window)
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

def compute_dist(a, b):
    total = 0
    for i in range(a.shape[1]):
        for j in range(b.shape[1]):
            a_sum = a[:, i].sum() == 0
            b_sum = b[:, j].sum() == 0

            if a[:, i].sum() == 0:
                total += np.linalg.norm(b[:,j])
            elif b[:, j].sum() == 0:
                total += np.linalg.norm(b[:,j])
            else:
                total += sp.distance.cosine(a[:,i].flatten(), b[:,j].flatten())
    return float(total) / (a.shape[1] * b.shape[1])
