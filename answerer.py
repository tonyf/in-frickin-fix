import numpy as np
import spacy

class Answerer(object):

    def __init__(self, doc, k):
        self.k = k
        self.nlp = spacy.load('en')
        self.doc = nlp(doc)
        self.doc_matrix = get_doc_matrix(self.doc, self.k)

    def get_doc_matrix(doc, k):
        sentences = []
        for sent in doc.sents:
            sentences.append(get_sentence_matrix(sent, k))
        return sentences

    def get_sentence_matrix(s, k):
        n = len(s) > k ? len(s) : k
        matrix = np.zeros((s[0].size, n))
        for i in len(q):
            matrix[:,i] = s[i].vector
        if n > k:
            # k-max pool
        return matrix

    def find_answer_sentence(self, q_matrix):
        return

    def get_answer(self, question):
        q = nlp(question)
        q_matrix = get_sentence_matrix()
        return
