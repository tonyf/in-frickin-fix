import numpy as np
import scipy.spatial as sp
import collections
import math
from q_classifier import QClassifier

Sentence = collections.namedtuple('Sentence', 'text matrix')
EMBEDDING_SIZE = 300

class Answerer(object):
    def __init__(self, set_dict, nlp):
        self.nlp = nlp
        self.set_dict = set_dict

    def find_answer_sentence(self, q, doc, window):
        matrix = get_doc_matrix(doc)
        smallest = matrix[0]
        s_dist = compute_dist(matrix[0].matrix, q)
        s_index = 0

        for i in range(len(matrix)):
            s = matrix[i]
            dist = compute_dist(s.matrix, q)
            if dist < s_dist:
                smallest = s
                s_dist = dist
                s_index = i
        step = int(math.floor(float(window) / 2))
        start = s_index-step if s_index-step > 0 else 0
        stop = s_index+step+1 if s_index+step < len(matrix) else len(matrix)
        return matrix[start:stop]

    def get_answer(self, question, window):
        q = self.nlp(question)
        m = get_sentence_matrix(q)
        
        qclassifier = QClassifier(q)
        qtype = qclassifier.type
        
        doc = self.find_probable_doc(q)
        
        answer = self.find_answer_sentence(m, doc, window)
        text = [x.text.strip() for x in answer]
        return ' '.join(text)

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
