import spacy

nlp = spacy.load('en')

def process_file(filepath):
    text, topic = None
    with open(filepath, 'r') as f:
        text = f.read()
        text = text.decode('utf-8')
        topic = text[0]
    return nlp(text)
