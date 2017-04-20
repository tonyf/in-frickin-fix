from collections import defaultdict, namedtuple
from document_classifier.classifier import *
import scipy.spatial as sp
import numpy as np

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
    matrix = np.zeros((EMBEDDING_SIZE, 1))
    matrix[:,0] = s.vector
    return matrix

def ent2categories(entity):
    # TODO: Map spacy entities to categories
    return []

def get_category_docs(doc_dict, categories):
    docs = []
    for c in categories:
        docs.extend(doc_dict[c])
    return docs

def compute_dist(a, b):
    return 0.5 * windowed_dist(a, b, 1) + 0.5 * windowed_dist(a, b, 3)

def windowed_dist(a, b, window):
    total = 0
    normalize_factor = 0
    for i in xrange(0, a.shape[1], window):
        for j in xrange(0, b.shape[1], window):
            a_sum = a[:, i:i+window].sum(axis=1)
            b_sum = b[:, j:j+window].sum(axis=1)
            normalize_factor += 1

            if a_sum.sum() == 0:
                total += np.linalg.norm(b[:,j])
            elif b_sum.sum() == 0:
                total += np.linalg.norm(b[:,j])
            else:
                total += sp.distance.cosine(a_sum.flatten(), b_sum.flatten())
    return total / normalize_factor

def get_vector(a, window):
    total = 0
    for i in xrange(0, a.shape[1]):
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
