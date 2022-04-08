"""
We create several rules to filter the sentences
which are unlikely to contain useful information
for the PR title generation
"""

from sklearn.utils import shuffle
import pandas as pd
import logging
import os
import re
import ujson
import argparse
import random
from tqdm import tqdm
import nltk
from statistics import mean, median

random.seed(941207)

START_DESCRIPTION = '<desc>'
END_DESCRIPTION = '</desc>'
START_COMMIT = '<cmt>'
END_COMMIT = '</cmt>'
START_ISSUE = '<iss>'
END_ISSUE = '</iss>'

EXTRCT_TOKENS = [START_DESCRIPTION, END_DESCRIPTION, \
START_COMMIT, END_COMMIT, START_ISSUE, END_ISSUE]


def remove_special_tokens(data_file):
    df = pd.read_csv(data_file, usecols=["text", "title"])
    print(df.shape)

    for index, row in tqdm(df.iterrows()):
        ori_text = row['text']
        
        text = re.sub("<desc>", "", ori_text)
        text = re.sub('</desc>', '.', text)

        text = re.sub("<cmt>", "", text)
        text = re.sub('</cmt>', '.', text)

        text = re.sub("<iss>", "", text)
        text = re.sub("</iss>", '.', text)
        df.loc[index, 'text'] = text.strip()

    os.makedirs('../data/PRTiger/v25/', exist_ok=True)
    df.to_csv('../data/PRTiger/v25/with-dot.csv')


def count_cmt():
    file = '../data/PRTiger/v25/no-template-final.csv'
    
    df = pd.read_csv(file, usecols=["text", "title"])
    print(df.shape)
    cmt_count = list()

    for index, row in tqdm(df.iterrows()):
        text = row['text']

        if len(re.findall('<cmt>(.+?)</cmt>', text)) > 0:
            cmt_count.append(len(re.findall('<cmt>(.+?)</cmt>', text)))
        else:
            print('ahahhaha')
    
    print('median: {}'.format(median(cmt_count)))
    print('mean: {}'.format(mean(cmt_count)))


def count_iss():
    file = '../data/PRTiger/v25/no-template-final.csv'
    
    df = pd.read_csv(file, usecols=["text", "title"])
    print(df.shape)
    iss_count = list()

    for index, row in tqdm(df.iterrows()):
        text = row['text']

        if len(re.findall('<iss>(.+?)</iss>', text)) > 0:
            iss_count.append(len(re.findall('<iss>(.+?)</iss>', text)))
        else:
            iss_count.append(0)
    
    print('median: {}'.format(median(iss_count)))
    print('mean: {}'.format(mean(iss_count)))

def count_desc():
    file = '../data/PRTiger/v25/no-template-final.csv'
    
    df = pd.read_csv(file, usecols=["text", "title"])
    print(df.shape)
    desc_count = 0

    for index, row in tqdm(df.iterrows()):
        text = row['text']

        if len(re.findall('<desc>(.+?)</desc>', text)) > 0:
            desc_count += 1
    
    print('# of PRs with a description {}'.format(desc_count))

def remove_improper_body(data_file):
    df = pd.read_csv(data_file, usecols=["text", "title"])
    improp_count = 0
    drop_index = list()

    for index, row in tqdm(df.iterrows()):
        cur_body = row['text']
        body_tokenize = nltk.word_tokenize(cur_body)
        # removing punctuation
        body_words  = [x.lower() for x in body_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]

        if len(body_words) < 30:
            improp_count += 1
            drop_index.append(index)
        elif len(body_words) > 1000:
            improp_count += 1
            drop_index.append(index)
    
    df = df.drop(df.index[drop_index])
    df.to_csv('../data/PRTiger/v25/no-token-template-final.csv', index=False)

    with_token_df = pd.read_csv('../data/PRTiger/v25/no-template.csv', usecols=["text", "title"])
    with_token_df = with_token_df.drop(with_token_df.index[drop_index])
    with_token_df.to_csv('../data/PRTiger/v25/no-template-final.csv', index=False)

    print(improp_count)


def data_statistics(data_folder):
    sources, titles = list(), list()

    for var in ['train', 'valid', 'test']:
        df = pd.read_csv(data_folder + '{}.csv'.format(var), usecols=["text", "summary"])
        title_word_count, body_word_count = [], []

        for index, row in tqdm(df.iterrows()):
            cur_body = row['text']
            # body_tokenize = nltk.word_tokenize(cur_body)
            # body_words  = [x.lower() for x in body_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]
            # body_word_count.append(len(body_words))
            body_word_count.append(len(cur_body.split()))

            cur_title = row['summary']
            # title_tokenize = nltk.word_tokenize(cur_title)
            # # removing punctuation
            # title_words = [x.lower() for x in title_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]
            # title_word_count.append(len(title_words))
            title_word_count.append(len(cur_title.split()))

        sources.extend(body_word_count)
        titles.extend(title_word_count)

        print('variant type is {}'.format(var))
        print('body avg words is {}'.format(mean(body_word_count)))
        print('title avg words is {}'.format(mean(title_word_count)))
    print('average tokens in the source: {}'.format(mean(sources)))
    print('average tokens in the titles: {}'.format(mean(titles)))


def pred_statistics(data_folder):
    for file in os.listdir(data_folder):
        print(file)
        with open(data_folder + file) as f:
            lines = f.readlines()
        
        title_word_count = list()

        for line in lines:
            # title_words = [x.lower() for x in line if re.match("\S*[A-Za-z0-9]+\S*", x)]
            title_words = line.strip().split()
            title_word_count.append(len(title_words))

        print('avg words: {}'.format(mean(title_word_count)))


def split_data(data_file, ver_num, no_token_flag=False):
    df = pd.read_csv(data_file, usecols=['text', 'title'])
    title_list = df['title'].tolist()
    body_list = df['text'].tolist()

    title_list, body_list = shuffle(title_list, body_list, random_state=941207)

    sep1 = int(len(title_list) * 0.8)
    sep2 = int(len(title_list) * 0.9)
    
    # sample refining procedure. - to filter out unsuitable samples according to three heuristic rules

    logging.info('splitting the data')

    valid_prs_train_body = []
    valid_prs_train_title = []
    valid_prs_val_body = []
    valid_prs_val_title = []
    valid_prs_test_body = []
    valid_prs_test_title  = []

    for idx in range(len(title_list)):
        if idx % 10000 == 0:
            print("current idx:", idx, "/", len(title_list), 
                "valid_train:", len(valid_prs_train_body), 
                "valid_val:", len(valid_prs_val_body), 
                "valid_test:", len(valid_prs_test_body))

        if idx < sep1:
            valid_prs_train_body.append(body_list[idx])
            valid_prs_train_title.append(title_list[idx])
        elif idx < sep2:
            valid_prs_val_body.append(body_list[idx])
            valid_prs_val_title.append(title_list[idx])
        else:
            valid_prs_test_body.append(body_list[idx])
            valid_prs_test_title.append(title_list[idx])

    os.makedirs('../data/PRTiger/v{}/'.format(ver_num), exist_ok=True)

    if no_token_flag:
        os.makedirs("../data/PRTiger/v{}/no-token/".format(ver_num), exist_ok=True)

        pd.DataFrame({'text': valid_prs_train_body, \
            'summary': valid_prs_train_title}).to_csv("../data/PRTiger/v{}/no-token/train.csv".format(ver_num))
        
        pd.DataFrame({'text': valid_prs_val_body, \
            'summary': valid_prs_val_title}).to_csv("../data/PRTiger/v{}/no-token/valid.csv".format(ver_num))
            
        pd.DataFrame({'text': valid_prs_test_body, \
            'summary': valid_prs_test_title}).to_csv("../data/PRTiger/v{}/no-token/test.csv".format(ver_num))
    else:
        os.makedirs("../data/PRTiger/v{}/with-dot/".format(ver_num), exist_ok=True)

        pd.DataFrame({'text': valid_prs_train_body, \
            'summary': valid_prs_train_title}).to_csv("../data/PRTiger/v{}/with-dot/train.csv".format(ver_num))

        pd.DataFrame({'text': valid_prs_val_body, \
            'summary': valid_prs_val_title}).to_csv("../data/PRTiger/v{}/with-dot/valid.csv".format(ver_num))
            
        pd.DataFrame({'text': valid_prs_test_body, \
            'summary': valid_prs_test_title}).to_csv("../data/PRTiger/v{}/with-dot/test.csv".format(ver_num))

    print("refinement done. obtain", len(valid_prs_train_body), ",", len(valid_prs_val_body), \
        ",", len(valid_prs_test_body), "issues for training, validation and testing.")


def check_templates():
    PR_folder = '../data/exp-pull-request'
    template_folder = '../data/PR-templates'
    repos_with_tmpt = set()

    for file in os.listdir(template_folder):
        repos_with_tmpt.add(os.path.splitext(file)[0])

    repos_no_tmpt = set()
    with_tmpt = 0
    total = 0
    for dir in os.listdir(PR_folder):
        total += 1
        if not dir in repos_with_tmpt:
            repos_no_tmpt.add(dir)
        else:
            with_tmpt += 1
    print('total: {}'.format(total))
    print(len(repos_no_tmpt))
    print('with a template: {}'.format(with_tmpt))


emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE)


def analyze_PR_template():
    template_folder = '../data/PR-templates/'
    template_names = set(["pull_request_template.md", \
        "pull_request_template", "pr.md"])
    temp_info = list()

    for file in os.listdir(template_folder):
        with open(template_folder + file) as f:
            cur_json = ujson.load(f)
        tmp_cnt = len(cur_json['data']["repository"]["pullRequestTemplates"])
        found_temp = False

        for i in range(tmp_cnt):
            if cur_json['data']["repository"]["pullRequestTemplates"][i]["filename"].lower() in template_names:
                found_temp = True
                body = cur_json['data']["repository"]["pullRequestTemplates"][i]['body']
                sents = body.split('\n')
                
                for sent in sents:
                    stripped_sent = sent.strip()

                    stripped_sent = emoji_pattern.sub(r'', stripped_sent)

                    ## non-English
                    try:
                        stripped_sent.encode(encoding='utf-8').decode('ascii')
                    except UnicodeDecodeError:
                        continue

                    stripped_sent = stripped_sent.strip()

                    if re.findall("^<!--", stripped_sent):
                        continue
                    if re.findall("^-->", stripped_sent):
                        continue
                    if re.findall("-->$", stripped_sent):
                        continue
                    if re.findall("^- \[ \]", stripped_sent):
                        continue

                    if re.findall("^\* \[ \]", stripped_sent):
                        continue

                    if re.findall("^\* \[x\]", stripped_sent):
                        continue

                    if re.findall("^\[[0-9]\]", stripped_sent):
                        continue

                    if re.findall("^- \[\]", stripped_sent):
                        continue

                    if re.findall(r'(https?://[^\s]+)', stripped_sent):
                        continue

                    if re.findall("\[ \]", stripped_sent):
                        continue

                    if re.findall("\| .* \| .*", stripped_sent):
                        continue

                    if re.findall("\| .* \|", stripped_sent):
                        continue

                    if len(stripped_sent) > 0:
                        temp_info.append(stripped_sent)

                    # if re.findall("^#", sent.strip()):
                        # temp_info.append((re.sub("^[#]*\s", '', sent)).lower())

        if not found_temp:
            print('no template: {}'.format(file))
            os.unlink(template_folder + file)
            

    temp_info.sort()
    with open('temp_heading.txt', 'w') as f:
        for info in temp_info:
            f.write(info)
            f.write('\n')

def count_PRs():
    count = 0
    for dir in os.listdir('../data/pull-request/'):
        logging.info(dir)

        for json_file in os.listdir('../data/pull-request/' + dir):
            count += 1
    print(count)


if __name__ == '__main__':
    # count_cmt()
    # count_iss()
    # count_desc()
    # count_PRs()
    # parser = argparse.ArgumentParser(description='pass the ver num')
    # parser.add_argument('--ver', help='version number', required=True)

    # args = parser.parse_args()

    # ver_num = int(args.ver)

    # pred_statistics('../predicted/')
    # remove_special_tokens('../data/PRTiger/v25/no-template-final.csv')

    # remove_improper_body('../data/PRTiger/v25/no-token-template.csv')
    # data_statistics('../data/PRTiger/v25/no-token/')

    # split_data('../data/PRTiger/v{}/with-dot.csv'.format(ver_num), ver_num)

    check_templates()
    # analyze_PR_template()