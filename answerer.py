import numpy as np
import scipy.spatial as sp
import spacy
import collections

Sentence = collections.namedtuple('Sentence', 'text matrix')
EMBEDDING_SIZE = 300

class Answerer(object):
    def __init__(self, doc):
        self.nlp = spacy.load('en')
        self.doc = self.nlp(doc)
        self.matrix = get_doc_matrix(self.doc)

    def find_answer_sentence(self, q):
        smallest = self.matrix[0]
        s_dist = compute_dist(self.matrix[0].matrix, q)
        for sent in self.matrix:
            dist = compute_dist(sent.matrix, q)
            if dist < s_dist:
                smallest = sent
                s_dist = dist
        return smallest

    def get_answer(self, question):
        q = self.nlp(question)
        m = get_sentence_matrix(q)
        answer = self.find_answer_sentence(m)
        return answer.text

def get_doc_matrix(doc):
    sentences = []
    for sent in doc.sents:
        s = Sentence(text=sent.text, matrix=get_sentence_matrix(sent))
        sentences.append(s)
    return sentences

def get_sentence_matrix(s):
    n = len(s)
    matrix = np.zeros((EMBEDDING_SIZE, n))
    for i in range(n):
         matrix[:,i] = s[i].vector[:]
    # K-Max Pooling
    # if n > k:
    #     summed = np.sum(matrix, axis=0)
    #     idx = summed.argsort()
    #     matrix = np.take(matrix, idx, axis=1)[:,:k]
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
