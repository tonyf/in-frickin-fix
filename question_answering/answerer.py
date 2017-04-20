import math
import numpy as np
import scipy.spatial as sp
import collections

from doc_utils import *
import q_classifier as qc

class Answerer(object):
    def __init__(self, doc, nlp):
        self.nlp = nlp
        self.doc = doc
        self.matrix = get_doc_matrix(doc)

    def closest_sentences(self, q, qtype, window):
        m = get_sentence_matrix(q)
        smallest = {}

        for i in range(len(self.matrix)):
            s = self.matrix[i]
            dist = compute_dist(s.matrix, m).item()
            if qc.has_type(s.sp_sent, qtype):
                smallest[dist] = s
        keys = smallest.keys()
        keys.sort()
        return [smallest[key] for key in keys]

    def find_closest_sentence(self, q, qtype, window):
        sentences = self.closest_sentences(q, qtype, window)[:5]
        ner_answer = self.find_ner_sentence(sentences, q, qtype)
        smallest_answer = sentences[0]
        if ner_answer:
            return ner_answer.sp_sent
        return smallest_answer.sp_sent

    def find_ner_sentence(self, sents, q, qtype):
        # TODO: Numbers
        q_ents = get_ents_in_sent(q.sents.next())
        q_ents = [x for x in q_ents if x.label_ in ["DATE", "QUANTITY"]]
        for sent in sents:
            s_ents = get_ents_in_sent(sent.sp_sent)
            s_ents = [x for x in s_ents if x.label_ in ["DATE", "QUANTITY"]]
            if s_ents.sort == q_ents.sort:
                return sent
        return None

    def get_answer(self, question, window, format_answer):
        q = self.nlp(question)
        qtype = qc.qclassify(q)
        answer = self.find_closest_sentence(q, qtype, window)
        templated_answer = qc.get_template(answer, q, qtype)
        if format_answer and templated_answer is not None:
            return templated_answer
        return answer
