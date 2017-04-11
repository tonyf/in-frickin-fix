import cPickle

from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

DATA_DIR = 'data/'
MODEL_PATH = 'doc_classifier.pkl'

class Classifier:
    def __init__():
        self.model = get_model()

    def predict(self, doc):
        return self.model.predict(doc)


def train_model():
    train = datasets.load_files(DATA_DIR)
    text_clf = Pipeline([('vect', CountVectorizer()),
                            ('tfidf', TfidfTransformer()),
                            ('clf', MultinomialNB()),
    model = text_clf.fit(train.data, train.target)
    return model


def save_model(model):
    with open(MODEL_PATH, 'wb') as f:
        cPickle.dump(model, f)

def load_model():
    model = None
    with open(MODEL_PATH, 'rb') as f:
        model = cPickle.load(f)
    return model

def get_model():
    model = load_model()
    if model is None:
        model = train_model()
        save_model(model)
    return model
