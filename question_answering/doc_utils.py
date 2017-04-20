from collections import defaultdict, namedtuple
from document_classifier.classifier import *
from operator import itemgetter
import scipy.spatial as sp
import numpy as np
import math

TOPIC_SIZE = 200
EMBEDDING_SIZE = 300
Sentence = namedtuple('Sentence', 'text sp_sent matrix')

OVERLAP = 1
L3_GRAM = 0.08
L5_GRAM = 0.08
L7_GRAM = 0.08
LF_GRAM = 0.75

def get_doc_title(doc):
    # TODO: reliably parse title from document
    return ""

def get_doc_matrix(doc):
    sentences = []
    for sent in doc.sents:
        s = Sentence(text=sent.text, sp_sent=sent, matrix=get_sentence_matrix(sent))
        sentences.append(s)
    return sentences

def get_sentence_matrix(s):
    n = len(s)
    matrix = np.zeros((EMBEDDING_SIZE, n))
    for i in range(n):
        matrix[:,i] = s[i].vector
    return matrix

def ent2categories(entity):
    # TODO: Map spacy entities to categories
    return []

def get_category_docs(doc_dict, categories):
    docs = []
    for c in categories:
        docs.extend(doc_dict[c])
    return docs

def get_norm(a):
    a = a.sum(axis=0)
    return np.count_nonzero(a)

def compute_dist(a, b):
    return 0.5 * sentence_distance(a, b) + 0.25 * windowed_distance(a, b, 3) + 0.25 * windowed_distance(a, b, 5)

def windowed_distance(a, b, window, mode='min'):
    total = 0
    a_norm = 0
    b_norm = 0

    a_sum = np.zeros((EMBEDDING_SIZE, window))
    b_sum = np.zeros((EMBEDDING_SIZE, window))

    sums = []
    for i in xrange(0, a.shape[1], window):
        for j in xrange(0, b.shape[1], window):
            a_sum = a[:, i:i+window]
            b_sum = b[:, j:j+window]

            a_norm = get_norm(a_sum)
            b_norm = get_norm(b_sum)

            if a_norm != 0 and b_norm != 0:
                a_vector = a_sum.sum(axis=1).flatten() / a_norm
                b_vector = b_sum.sum(axis=1).flatten() / b_norm
                sums.append( (a_vector, b_vector) )

    distances = [sp.distance.cosine(x[0], x[1]) for x in sums]
    if mode == 'min':
        return min(distances)
    return sum(distances) / len(distances)


def sentence_distance(a, b):
    total = 0
    a = a.sum(axis=1)
    b = b.sum(axis=1)
    return sp.distance.cosine(a.flatten(), b.flatten())
