import math
import numpy as np
import scipy.spatial as sp

from doc_utils import *
from q_classifier import *

class Answerer(object):
    def __init__(self, doc, nlp):
        self.nlp = nlp
        self.doc = doc
        self.matrix = get_doc_matrix(doc)

    def find_answer_sentence(self, question, window):
        smallest = self.matrix[0]
        q = get_sentence_matrix(question)
        s_dist = compute_dist(self.matrix[0].matrix, q)
        s_index = 0
        qtype = qclassify(question)

        for i in range(len(self.matrix)):
            s = self.matrix[i]
            dist = compute_dist(s.matrix, q)
            if dist < s_dist and has_type(s, qtype):
                smallest = s
                s_dist = dist
                s_index = i
        step = int(math.floor(float(window) / 2))
        start = s_index-step if s_index-step > 0 else 0
        stop = s_index+step+1 if s_index+step < len(self.matrix) else len(self.matrix)
        return self.matrix[start:stop]

    def get_answer(self, question, window):
        q = self.nlp(question)
        answer = self.find_answer_sentence(q, window)
        text = [x.text.strip() for x in answer]
        return ' '.join(text)
