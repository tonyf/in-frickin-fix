import math
import numpy as np
import scipy.spatial as sp
import collections
import operator

from doc_utils import *
import q_classifier as qc

class Answerer(object):
    def __init__(self, doc, nlp):
        self.nlp = nlp
        self.doc = doc
        self.matrix = get_doc_matrix(doc)

    def closest_sentences(self, q, qtype):
        m = get_sentence_matrix(q)
        smallest = []

        for i in range(len(self.matrix)):
            s = self.matrix[i]
            dist = q.similarity(s.sp_sent)
            if qc.has_type(s.sp_sent, qtype):
                smallest.append((s, dist))

        smallest.sort(key=lambda x: x[1], reverse=True)
        return [key for key, value in smallest]

    def find_closest_sentence(self, q, qtype):
        sentences = self.closest_sentences(q, qtype)
        num = min(len(sentences),20)
        sentences = sentences[:num]
        # for sent in sentences:
            # print sent.sp_sent
        ner_answer = self.find_ner_sentence(sentences, q, qtype)
        smallest_answer = sentences[0]
        if ner_answer:
            return ner_answer.sp_sent
        return smallest_answer.sp_sent

    def check_ents(self, q_ents, a_ents):
        q_tokens = set([x.text for x in q_ents])
        a_tokens = set([x.text for x in a_ents])
        for q in q_tokens:
            if q not in a_tokens:
                return False
        return True

    def find_ner_sentence(self, sents, q, qtype):
        # TODO: Numbers
        q_ents = get_ents(q.sents.next())
        for sent in sents:
            s_ents = get_ents(sent.sp_sent)
            # print sent.sp_sent
            if self.check_ents(q_ents, s_ents):
                return sent
        return None

    def get_answer(self, question, window, format_answer):
        q = self.nlp(question)
        qtype = qc.qclassify(q)
        answer = self.find_closest_sentence(q, qtype)
        templated_answer = qc.get_template(answer, q, qtype)
        if format_answer and templated_answer is not None:
            return templated_answer
        return answer
