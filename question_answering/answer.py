import spacy
import sys
import argparse
from answerer import Answerer
from lib.preprocess import *

# Example: python main.py ./data

def test():
    nlp = spacy.load("en")

    root_dir = sys.argv[1]
    sets = ["set1"]
    set_dict = preprocess_docs(root_dir, sets, nlp)
    #doc1 = set_dict[sets[0]][0]

    A = Answerer(set_dict, nlp)
    if use_terminal:
        questions = [unicode(raw_input("Question: "))]
    else:
        '''
        questions =\
            [
                u"What does the dog like to chase?",
                u"Is London a famous city?",
                u"Is Clint Dempsey a famous city?",
                u"Who was Clint Dempsey?",
                u"What does Clint Dempsey think about Communism?",
                u"Is Clint Dempsey in a good mood today?"
            ]
        '''
        questions =\
            [
                u"Who is Lionel Messi?",
                u"Where was Clint Dempsey born?",
                u"Is David Beckham American?",
                u"Which team won the league title in 2000?"
            ]

    for question in questions:
            answer = A.get_answer(question, 3)
            print "Q: {0} | A: {1}".format(question, answer)


def answer_questions(doc_text, questions, format_answer):
    nlp = spacy.load("en")
    doc = preprocess(doc_text, nlp)
    A = Answerer(doc, nlp)
    for q in questions:
        if len(q) == 0:
            print " "
        else:
            answer = A.get_answer(q, 0, format_answer)
            print answer

def main():
    _, doc_text = read_doc(sys.argv[1])
    questions = read_questions(sys.argv[2])
    format_answer = True
    if len(sys.argv) > 3:
        format_answer = not bool(sys.argv[3])
    answer_questions(doc_text, questions, format_answer)


if __name__ == '__main__':
    main()
