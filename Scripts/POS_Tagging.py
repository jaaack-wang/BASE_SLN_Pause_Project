# This script is originally made up of several separate scripts that were causally written, which deals with the following four tasks:
# 1. replace all the BASE tags (e.g., <u>, </u>, <pause>) plus filled pauses (denoted by '#') with an unique placeholder (I made it “空”)；
# 2. POS tag the processed texts that contain placeholders;
# 3. replace the placeholders back with their original tags;
# 4. remake the xml version of the POS tagged BASE.


# 1. replace all the BASE tags (e.g., <u>, </u>, <pause>) plus filled pauses (denoted by '#') with an unique placeholder (I made it “空”)；
# The original script for this task was lost, but it can be easily done by using regex to change a tag into “空"
# The expression I used for this is re.sub(r'(#|<trunc>[^>]>|<distinct[^>]+>|<[^>]+>|\[[^]]+]|{[^}]+})', ‘空', a_BASE_file)。Also see step 3 below.
# Please note that "a_BASE_file" refers to only the body part of the original xml BASE file that has been saved in txt format.
# This was done by using BeautifulSoup. a_BASE_file = BeautifulSoup(open(the_path_to_the_xml_BASE_file), 'lxml').find('body') or.find('text')


# 2. POS tag the processed texts that contain placeholders
# The original script for this task was also lost, but the POS tagging function was built something like this:


import re
import json
from stanfordcorenlp import StanfordCoreNLP

# loading Stanford tagger
nlp = StanfordCoreNLP("/Users/wzx/p_package/stanford-corenlp-4.1.0")
# setting the properties for the nlp annotator
props = {'annotators': 'tokenize,ssplit,pos,lemma', 'tokenize.whitespace': 'true', 'outputFormat': 'json'}


# split basic contractions as the whitespace is turned on for tokenizing
def text_splitting(raw_text):

    text = " " + raw_text + " "

    # patterns for cleaning the raw texts: targeted patterns + replaced patterns
    splitter = {

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
  
  
  
 # 3. replace the placeholders back with their original tags;

import re

input_path = '/Users/wzx/Downloads/BASE/BASE_Modified/Original_TXT/{}.txt'
tag_path = '/Users/wzx/Downloads/Tagged/{}.txt'
output_path = '/Users/wzx/Downloads/Tagged/Modified/{}.txt'


def file_name(sub, lct_idx):
    filename = '%slct%03d' % (sub, lct_idx)
    return filename


def main():
    subs = ['ah', 'ls', 'ss', 'ps']
    for sub in subs:
        idx = 0
        for _ in range(40):
            idx += 1
            filename = file_name(sub, idx)
            path_input = input_path.format(filename)

            text = open(path_input).read()
            place_holder = re.findall(r'(#|<trunc>[^>]>|<distinct[^>]+>|<[^>]+>|\[[^]]+]|{[^}]+})', text)

            path_tag = tag_path.format(filename)
            tagged_text = open(path_tag).read()

            for ph in place_holder:
                tagged_text = re.sub(r'空_\S+', ph, tagged_text, count=1)

            f = open(output_path.format(filename), 'w')
            f.write(str(tagged_text))
            f.close()


if __name__ == '__main__':
    main()



# 4. remake the xml version of the POS tagged BASE.

from nltk import RegexpTokenizer
from lxml import etree
from bs4 import BeautifulSoup


input_path = '/Users/wzx/Downloads/Test/{}.txt'
output_path = '/Users/wzx/Downloads/TestAgain/{}.xml'
path11 = '/Users/wzx/Downloads/BASE/{}/{}.xml'


subs = ['ah', 'ls', 'ss', 'ps']
for sub in subs:
    idx = 0
    for _ in range(40):
        idx += 1
        filename = '%slct%03d' % (sub, idx)
        path = input_path.format(filename)
        path1 = path11.format(sub, filename)
        text = open(path).read()
        soup = BeautifulSoup(open(path1), 'xml')
        
        # header comes from original BASE files directly 
        header = soup.find('teiHeader').prettify()

        content = '<TEI.2>' + header + text + '</TEI.2>'
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(content, parser=parser)
        tree = etree.ElementTree(root)
        tree.write(output_path.format(filename))
