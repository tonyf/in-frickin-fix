from collections import defaultdict, namedtuple

Sentence = collections.namedtuple('Sentence', 'text matrix')

def parse_docs(docs):
    doc_dict = defaultdict(list)
    classifier = DocClassifier()
    for doc in docs
        category = classifier.predict(doc.text)
        doc_dict[category].append(doc)
    return doc_dict

def get_doc_title(doc):
    # TODO: reliably parse title from document
    return ""

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
