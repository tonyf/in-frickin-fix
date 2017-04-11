import sys
from wikiapi import WikiApi
from os.path import basename
# Given a text file
# download all the wikipedia articles in that category.
# put files into a foler with category name

wiki = WikiApi()

def write_doc_file(title, output_folder):
    results = wiki.find(title)
    if results:
        article = wiki.get_article(results[0])
        filepath = output_folder + article.heading.strip() + '.txt'
        content = article.content.encode('utf-8').strip()
        output = open(filepath, 'w')
        output.write(content)
        output.close

def get_titles(input_file):
    titles = []
    with open(input_file) as f:
        titles = f.readlines()
    titles = [t.strip() for t in titles]
    return titles

def main():
    input_file = sys.argv[1]
    article_class = input_file.split('.')[0]
    output_folder = 'data/' + article_class + '/'
    titles = get_titles(input_file)
    for title in titles:
        write_doc_file(title, output_folder)
    print('Done.')

if __name__ == '__main__':
    main()