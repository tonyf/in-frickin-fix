import spacy
import sys
from answerer import Answerer
from preprocess import preprocess_docs

# Example: python main.py ./data

def main(use_terminal):
    nlp = spacy.load("en")

    root_dir = sys.argv[1]
    sets = ["test_set"]
    set_dict = preprocess_docs(root_dir, sets, nlp)
    doc1 = set_dict[sets[0]][0]

    A = Answerer(doc1, nlp)
    if use_terminal:
        questions = [unicode(raw_input("Question: "))]
    else:
        questions =\
            [
                u"What does the dog like to chase?",
                u"Is London a famous city?",
                u"Is Clint Dempsey a famous city?",
                u"Who was Clint Dempsey?",
                u"What does Clint Dempsey think about Communism?",
                u"Is Clint Dempsey in a good mood today?"
            ]
    
    for question in questions:
            answer = A.get_answer(question)
            print "Q: {0} | A: {1}".format(question, answer.strip())
            

if __name__ == '__main__':
    use_terminal = True
    main(use_terminal)
