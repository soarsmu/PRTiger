"""
Modified from https://github.com/qiuweipku/Plain_language_summarization/blob/main/CDSR_data/oracle_extractive.py

"""

from nltk.tokenize import sent_tokenize
from rouge import Rouge
import numpy as np
import re
import pandas as pd

def split_sentences(text):
    sents = list()

    if len(re.findall('<desc>([\w\W]*)</desc>', text)) > 0:
        desc = re.findall('<desc>([\w\W]*)</desc>', text)[0].strip()
        sents.extend(sent_tokenize(desc))
    
    if len(re.findall('<cmt>(.+?)</cmt>', text)) > 0:
        for cmt_item in re.findall('<cmt>(.+?)</cmt>', text):
            sents.extend(sent_tokenize(cmt_item.strip()))
    
    if len(re.findall('<iss>(.+?)</iss>', text)) > 0:
        for iss_item in re.findall('<iss>(.+?)</iss>', text):
            sents.extend(sent_tokenize(iss_item.strip()))
            
    return sents

if __name__ == '__main__':
    rouge = Rouge()

    target_all = []

    with open('../iTAPE/data/v25/title.test.txt','r+') as f:
        for line in f.readlines():
            target_all.append(line.strip())

    print(len(target_all))

    f_out = open('./real-test_oracle_extractive.txt', 'w')

    df = pd.read_csv('../data/PRTiger/v25/test.csv')

    for index, row in df.iterrows():
        source = row['text']
        target = target_all[index]

        extracted_abstract = ''

        source_sent = split_sentences(source)

        score_temp = []
        for src_s in source_sent:
            try:
                score_temp.append(rouge.get_scores(src_s, target)[0]['rouge-2']['f'])
            except:
                score_temp.append(0)
        extracted_abstract += source_sent[np.argmax(np.array(score_temp))]

        f_out.write(extracted_abstract + '\n')
        
    f_out.close()