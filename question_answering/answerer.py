import math
import numpy as np
import scipy.spatial as sp

from doc_utils import *
import q_classifier as qc

class Answerer(object):
    def __init__(self, doc, nlp):
        self.nlp = nlp
        self.doc = doc
        self.matrix = get_doc_matrix(doc)

    def find_answer_sentence(self, q, qtype, window):
        m = get_sentence_matrix(q)
        smallest = self.matrix[0]
        s_dist = compute_dist(self.matrix[0].matrix, m)
        s_index = 0


        for i in range(len(self.matrix)):
            s = self.matrix[i]
            dist = compute_dist(s.matrix, m)
            if dist < s_dist and qc.has_type(s.sp_sent, qtype):
                smallest = s
                s_dist = dist
                s_index = i
        #step = int(math.floor(float(window) / 2))
        #start = s_index-step if s_index-step > 0 else 0
        #stop = s_index+step+1 if s_index+step < len(self.matrix) else len(self.matrix)

        return smallest.sp_sent
        #return self.matrix[start:stop]

    def get_answer(self, question, window, format_answer):
        q = self.nlp(question)
        qtype = qc.qclassify(q)
        answer = self.find_answer_sentence(q, qtype, window)
        templated_answer = qc.get_template(answer, q, qtype)
        if format_answer and templated_answer is not None:
            return templated_answer
        return answer
