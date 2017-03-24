from answerer import Answerer
import sys

# Example: python main.py data/set1/a10.txt

def main():
    doc = None
    doc_file = sys.argv[1]

    with open(doc_file, 'r') as f:
        doc = f.read().decode('utf-8')

    A = Answerer(doc)
    question = raw_input("Question: ").decode('utf-8')
    print A.get_answer(question)


if __name__ == '__main__':
    main()
