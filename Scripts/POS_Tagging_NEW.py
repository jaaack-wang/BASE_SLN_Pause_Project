import re
import json
from os import listdir
from os.path import isfile, join
from stanfordcorenlp import StanfordCoreNLP
from bs4 import BeautifulSoup
from lxml import etree


# loading Stanford tagger
nlp = StanfordCoreNLP("/Users/wzx/p_package/stanford-corenlp-4.1.0")
# setting the properties for the nlp annotator
props = {'annotators': 'tokenize,ssplit,pos,lemma', 'tokenize.whitespace': 'true', 'outputFormat': 'json'}


def get_filenames_from_dir(file_dir):
    file_names = [f for f in listdir(file_dir) if isfile(join(file_dir, f)) if f != '.DS_Store']
    file_names.sort()
    return file_names


def text_splitting(raw_text):

    text = " " + raw_text + " "

    # patterns for cleaning the raw texts: targeted patterns + replaced patterns
    splitter = {

        # split basic contractions as the whitespace is turned on for tokenizing
        r"(\S+)(n't )": r"\1 \2",
        # r"(\S+)('[^t\s]\S? )": r"\1 \2",
        r"(\S+)('(m|re|s|d|ll|ve) )": r"\1 \2",
        r"(\S+s)(' )": r"\1 \2",
        r"(y')(\S+)": r"\1 \2",
        r"\bcannot\b": r"can not",

    }

    for target, replace in splitter.items():
        text = re.sub(target, replace, text, flags=re.IGNORECASE)

    # stripping extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def text_annotating(raw_text):
    split_text = text_splitting(raw_text)
    # change the global props value above to allow more annotations, such as ner, depparse
    annotated_text = nlp.annotate(split_text, properties=props)
    return annotated_text


def get_pos_tagged_text(raw_text):
    annotated_text = text_annotating(raw_text)
    annotated_text = json.loads(annotated_text)
    tagged_words = []
    for s in annotated_text['sentences']:
        for token in s['tokens']:
            tagged_words.append(
                token['originalText'] + "_" + token['pos']
            )
    return ' '.join(tagged_words)


def main():
    dire = '/Users/wzx/Downloads/BASE_XML/'
    filenames = get_filenames_from_dir(dire)
    for f in filenames:
        soup = BeautifulSoup(open(dire + f), 'xml')
        header = soup.find('teiHeader').prettify()
        body = str(soup.find('text'))

        base_tags = re.findall(r'(#|<trunc>[^>]+>|<[^>]+>|\[[^]]+]|{[^}]+})', body)
        changed_body = re.sub(r'(#|<trunc>[^>]+>|<[^>]+>|\[[^]]+]|{[^}]+})', '空', body)

        pos_tagged_body = get_pos_tagged_text(changed_body)

        for bt in base_tags:
            pos_tagged_body = re.sub(r'(空_\S+|空)', bt, pos_tagged_body, count=1)

        content = '<TEI.2>' + header + pos_tagged_body + '</TEI.2>'
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(content, parser=parser)
        tree = etree.ElementTree(root)
        tree.write('/Users/wzx/Downloads/TAGGED/' + f)
        print(f)


if __name__ == '__main__':
    main()

