import math
import numpy as np
import scipy.spatial as sp

from doc_utils import *
from q_classifier import *
from document_classifier.classifier import *

EMBEDDING_SIZE = 300
TOPIC_SIZE = 200

class Answerer(object):
    def __init__(self, docs, nlp):
        self.nlp = nlp
        self.docs = parse_docs(docs)

    def find_answer_doc(self, question):
        q = self.nlp(question)
        entity = None
        if q.ents:
            entity = q.ents[0]
        else:
            # No named entities, search with biggest vector
        categories = ent2categories(entity)
        category_docs = get_category_docs(self.docs, categories)

        best_doc = None
        max_sim = float("-inf")
        for doc in category_docs:
            title = get_doc_title(doc)
            sim = title.similarity(entity)
            if sim > max_sim:
                max_sim = sim:
                best_doc = doc
        return best_doc

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
        qtype = qclassify(q)
        m = get_sentence_matrix(q)
        doc = self.find_answer_doc(q)
        answer = self.find_answer_sentence(m, doc, window)
        text = [x.text.strip() for x in answer]
        return ' '.join(text)
