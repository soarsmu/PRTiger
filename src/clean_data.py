import os
import ujson
from datetime import datetime, timezone
from tqdm import tqdm
import re
from logger import init_logger
import logging
import nltk
import pandas as pd
import random
import sys
import argparse

random.seed(941207)

pr_folder = '../data/pull-request/'

end_date = '2021-12-31 23:59:59 +0000'

START_DESCRIPTION = '<desc>'
END_DESCRIPTION = '</desc>'
START_COMMIT = '<cmt>'
END_COMMIT = '</cmt>'
START_ISSUE = '<iss>'
END_ISSUE = '</iss>'


EXTRA_TOKENS = [
    START_DESCRIPTION,
    END_DESCRIPTION,
    START_COMMIT,
    END_COMMIT,
    START_ISSUE,
    END_ISSUE
]

def convert_to_utc(created_date):
    # e.g., "2018-07-26T20:32:20Z"
    dt = datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    return dt.strftime('%Y-%m-%d %H:%M:%S %z')

def filter_unmerged_issues():
    dir_list = os.listdir(pr_folder)
    useful = 0

    for dir in dir_list:
        after_date = 0
        unmerged = 0
        logging.info(dir)

        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)
            
            publish_date = cur_pr['publishedAt']

            creation_utc = convert_to_utc(created_date=publish_date)

            if creation_utc > end_date:
                # not within our time range
                os.unlink(pr_folder + dir + '/' + json_file)
                after_date += 1
                continue
            
            if not cur_pr['merged']:
                os.unlink(pr_folder + dir + '/' + json_file)
                unmerged += 1
                continue

            useful += 1
        logging.info('# of PRs after the date is {}'.format(after_date))
        logging.info('# of unmerged PRs is: {}'.format(unmerged))
        logging.info('# of left PRs is: {}'.format(useful))


def filter_future_commits():
    logging.info('filtering future')
    dir_list = os.listdir(pr_folder)
    total_one_commit = 0
    total_have_future_commits = 0
    left = 0

    for dir in dir_list:
        logging.info(dir)
        
        only_one_commit = 0
        count_have_future_commits = 0

        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)
            
            removed_commits = 0
            publish_date = cur_pr['publishedAt']
            count_commits = cur_pr['commits']['totalCount']
            
            if count_commits > 0:
                have_future_commits = False
                
                for i in range(min(count_commits, 30)):
                    if len(cur_pr['commits']['edges'][i]) > 0:
                        committed_date = cur_pr['commits']['edges'][i]['node']['commit']['committedDate']
                        # logging.info(json_file)

                        if committed_date > publish_date:
                            cur_pr['commits']['edges'][i] = {}
                            removed_commits += 1
                            have_future_commits = True

                    if have_future_commits:
                        with open(pr_folder + dir + '/' + json_file, 'w') as f:
                            ujson.dump(cur_pr, f)

                if have_future_commits:
                    # print('pre: {}'.format(count_commits))
                    count_have_future_commits += 1
                    # print('after: {}'.format(count_commits - removed_commits))
            
        logging.info('# of have future: {}\n'.format(count_have_future_commits))
        total_have_future_commits += count_have_future_commits
        total_one_commit += only_one_commit

    logging.info('total have future commits: {}'.format(total_have_future_commits))
    logging.info('PR left {}'.format(left))


def filter_improper_commit_length():
    """
    Removing the PRs with < 2 commits or > 20 commits
    """

    dir_list = os.listdir(pr_folder)
    total_less = 0
    total_more = 0

    for dir in dir_list:
        only_one_commit = 0
        more_than_20_commit = 0

        logging.info(dir)

        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)
            
            commits = cur_pr['commits']
            count_commits = commits['totalCount']

            commit_count = 0
            for i in range(min(count_commits, 30)):
                if len(cur_pr['commits']['edges'][i]) > 0:
                    commit_count += 1

            if commit_count > 20:
                more_than_20_commit += 1
                os.unlink(pr_folder + dir + '/' + json_file)
            elif commit_count < 2:
                only_one_commit += 1
                os.unlink(pr_folder + dir + '/' + json_file)

        
        logging.info('# of PRs with only one commit {}'.format(only_one_commit))
        logging.info('# of PRs with more than 20 commits {}'.format(more_than_20_commit))

        total_less += only_one_commit
        total_more += more_than_20_commit

    logging.info('in total # of PRs with only one commit {}'.format(total_less))
    logging.info('in total # of PRs with more than 20 commits {}'.format(total_more))


def isEnglish(s):
    """
    first remove emoji
    chech whether the rest part are English
    """

    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE)

    s = emoji_pattern.sub(r'', s) # no emoji

    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    
    return True


def filter_non_ascii(): 
    total_non_english = 0

    for dir in os.listdir(pr_folder):
        non_english = 0

        logging.info(dir)

        non_english_flag = False
        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)
            
            title = cur_pr['title']
            if not isEnglish(title):
                os.unlink(pr_folder + dir + '/' + json_file)                
                non_english += 1
                continue

            text = cur_pr['bodyText']
            if not isEnglish(text):
                os.unlink(pr_folder + dir + '/' + json_file)
                non_english += 1
                continue

            count_commits = cur_pr['commits']['totalCount']

            if count_commits > 0:
                for i in range(count_commits):
                    if len(cur_pr['commits']['edges'][i]) > 0:
                        if not isEnglish(cur_pr['commits']['edges'][i]['node']['commit']['message']):
                            os.unlink(pr_folder + dir + '/' + json_file)
                            non_english += 1
                            non_english_flag = True
                            break
                    else:
                        break
            
            if non_english_flag:
                continue

            issues = cur_pr['closingIssuesReferences']
            if len(issues['edges']) > 0:
                for i in range(len(issues['edges'])):
                    if not isEnglish(cur_pr['closingIssuesReferences']['edges'][i]['node']['title']):
                        os.unlink(pr_folder + dir + '/' + json_file)
                        non_english += 1
                        break
                    elif not isEnglish(cur_pr['closingIssuesReferences']['edges'][i]['node']['bodyText']):
                        os.unlink(pr_folder + dir + '/' + json_file)
                        non_english += 1
                        break


        logging.info('# of non English: {}\n'.format(non_english))
        
        total_non_english += non_english
        # logging.info(sample_list)
    
    logging.info('total # of non-english: {}'.format(total_non_english))


def filter_bot_written():
    dir_list = os.listdir(pr_folder)
    total_bot_written = 0

    for dir in dir_list:
        bot_written = 0

        logging.info(dir)

        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)
            
            author = cur_pr['author']
            if not author:
                continue
            
            if author['__typename'] == 'Bot':
                bot_written += 1
                os.unlink(pr_folder + dir + '/' + json_file)
        logging.info('bot written: {}'.format(bot_written))
        total_bot_written += bot_written

    logging.info(total_bot_written)


def count_associated_issues():
    dir_list = os.listdir(pr_folder)
    total_with_issues = 0
    total_prs = 0

    for dir in dir_list:
        have_issues = 0
        logging.info(dir)
        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)
            total_prs += 1
            issues = cur_pr['closingIssuesReferences']
            if len(issues['edges']) > 0:
                have_issues += len(issues['edges'])
        
        logging.info('# of PRs have associated issues {}'.format(have_issues))
        total_with_issues += have_issues

    logging.info('# with issues: {}'.format(total_with_issues))
    logging.info('# of PRs: {}'.format(total_prs))


def count_empty_body():
    dir_list = os.listdir(pr_folder)
    total_empty = 0

    for dir in dir_list:
        empty = 0

        logging.info(dir)

        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)
            
            text = cur_pr['bodyText']

            if len(text.strip()) == 0:
                empty += 1
        
        # logging.info('# of PRs without description {}'.format(empty))

        total_empty += empty

    logging.info('in total # of PRs without description {}'.format(total_empty))


def remove_empty_prs():
    empty_list = list()
    for dir in tqdm(os.listdir(pr_folder)):
        for json_file in os.listdir(pr_folder + dir):

            not_empty = False

            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)

            # check description
            if len(cur_pr['bodyText'].strip()) > 0:
                not_empty = True
                continue

            count_commits = cur_pr['commits']['totalCount']
            
            # check commits
            if count_commits > 0:
                for i in range(min(count_commits, 30)):
                    if len(cur_pr['commits']['edges'][i]) > 0:
                        committ_msg = cur_pr['commits']['edges'][i]['node']['commit']['message']

                        if len(committ_msg.strip()) > 0:
                            not_empty = True
                            break

            # check issues
            issues = cur_pr['closingIssuesReferences']
            if len(issues['edges']) > 0:
                for i in range(len(issues['edges'])):
                    if len(cur_pr['closingIssuesReferences']['edges'][i]['node']['title'] + \
                        cur_pr['closingIssuesReferences']['edges'][i]['node']['bodyText'].strip()) > 0:
                        not_empty = True

            if not not_empty:
                empty_list.append(pr_folder + dir + '/' + json_file)
                os.unlink(pr_folder + dir + '/' + json_file)

    print(len(empty_list))


# credit to iTAPE authors
def improve_title(pr_title):
    original_len = len(pr_title)
    pr_title = re.sub("^(\s*\[.*?\])+ \-?", "", pr_title) # remove starting [tag]
    pr_title = re.sub("^(\s*\(.*?\))+", "", pr_title) # remove starting (tag)

    pos = pr_title.find(": ")
    if -1 < pos < len(pr_title) - original_len / 2:
        pr_title = pr_title[pos + 1:].strip() # removing starting tag:

    pr_title = re.sub("^(\s*\[.*?\])+ \-?", "", pr_title) # remove starting [tag] x2
    pr_title = re.sub("^fixed #[0-9]+ -- ", "", pr_title) # remove Fix #...
    pr_title = re.sub("^fixed #[0-9]+", "", pr_title) # remove Fix #...

    pr_title = re.sub("(\*{1,})(.+?)(\*{1,})", lambda x: x.group(2), pr_title) # remove emphasis
    pr_title = re.sub('\`', '', pr_title)

    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE)

    pr_title = emoji_pattern.sub(r'', pr_title) # no emoji

    return pr_title.strip()

# credit to iTAPE authors
def rule1checker(pr_title):
    pr_title = improve_title(pr_title)
    pr_title_tokenize = nltk.word_tokenize(pr_title)
    pr_title_words = [x.lower() for x in pr_title_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]
    length = len(pr_title_words)

    if length < 5:
        return True
    if length > 15:
        return True
    # if len(re.findall("(https?|ftp)://[^\s/$.?#].[^\s]*", pr_title)) > 0:
        # return True
    return False


def rule2checker(pr_title):
    """
    removed templated titles
    """
    pr_title = pr_title.lower()

    reg = "^automated cherry pick of"
    if re.findall(reg, pr_title):
        return True
    if re.findall("^rolling up", pr_title):
        return True
    if re.findall("^rolling down", pr_title):
        return True
    if re.findall("^roll engine", pr_title):
        return True
    if re.findall("^rollup of", pr_title):
        return True
    if re.findall("^roll plugins", pr_title):
        return True
    if re.findall("^update live with current master", pr_title):
        return True
    if re.findall("^merge to", pr_title):
        return True
    if re.findall("^revert \"", pr_title):
        return True
    return False


# TITLE relation filter: title hit token count should meet threshold
def rule3checker(issue_title_words, issue_body_words):
    body_words_set = set(issue_body_words)
    cnt_each = 0
    for word in issue_title_words:
        if word in body_words_set:
            cnt_each += 1
    # less than 20% tokens hit, not one-sentence summarization
    if cnt_each <= len(issue_title_words) * 0.2:
        return True
    return False


emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE)


template_names = set(["pull_request_template.md", \
        "pull_request_template", "pr.md"])

def export_raw_data():
    title_list, body_list = list(), list()
    count = 0
    enhanced_bodies = list()
    # html_bodies = list()
    ## Exp 1
    # only_commits = list()
    ## Exp 2: commit + issue
    cmt_issues = list()

    for dir in tqdm(os.listdir(pr_folder)):
        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)

            improved_title = improve_title(cur_pr['title'])
            
            if rule1checker(improved_title) or rule2checker(improved_title):
                continue
            
            count += 1
            
            # 1. add bodyText
            cleaned_body_text = emoji_pattern.sub(r'', cur_pr['bodyText'])

            # html_body = cur_pr['bodyHTML']

            cur_body = cleaned_body_text
            
            enhanced_body = START_DESCRIPTION + ' ' + cleaned_body_text + ' ' + END_DESCRIPTION

            # 2. add commits
            count_commits = cur_pr['commits']['totalCount']
            
            only_commit = ''
            # check commits
            if count_commits > 0:
                for i in range(min(count_commits, 30)):
                    if len(cur_pr['commits']['edges'][i]) > 0:
                        commit_msg = cur_pr['commits']['edges'][i]['node']['commit']['message']

                        if len(commit_msg) > 0:
                            cleaned_commit = emoji_pattern.sub(r'', commit_msg)
                            # cleaned_commit = demoji.replace(commit_msg)
                            cur_body += " " + cleaned_commit

                            enhanced_body += ' ' + START_COMMIT + ' ' + cleaned_commit + ' ' + END_COMMIT
                            html_body += "\n" + commit_msg

                            if len(only_commit) == 0:
                                only_commit += START_COMMIT + ' ' + cleaned_commit + ' ' + END_COMMIT
                            else:
                                only_commit += " " + START_COMMIT + ' ' + cleaned_commit + ' ' + END_COMMIT

            cmt_iss = only_commit
            # check issues
            issues = cur_pr['closingIssuesReferences']
            if len(issues['edges']) > 0:
                for i in range(len(issues['edges'])):
                    if len(cur_pr['closingIssuesReferences']['edges'][i]['node']['title'] + \
                        cur_pr['closingIssuesReferences']['edges'][i]['node']['bodyText']) > 0:
                        issue_title = cur_pr['closingIssuesReferences']['edges'][i]['node']['title']
                        cleaned_title = emoji_pattern.sub(r'', issue_title)
                        # cleaned_title = demoji.replace(issue_title)

                        cur_body += " " + cleaned_title
                        enhanced_body += ' ' + START_ISSUE + ' ' + cleaned_title + ' ' + END_ISSUE
                        html_body += "\n" + issue_title
                        cmt_iss += ' ' + START_ISSUE + ' ' + cleaned_title + ' ' + END_ISSUE

                        # cur_body += " " + cur_pr['closingIssuesReferences']['edges'][i]['node']['bodyText']

            body_tokenize = nltk.word_tokenize(cur_body)
            body_words  = [x.lower() for x in body_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]

            if len(body_words) < 30:
                continue

            if len(body_words) > 1000:
                continue

            title_list.append(improved_title)
            body_list.append(cur_body)
            enhanced_bodies.append(enhanced_body)
            # html_bodies.append(html_body)
            cmt_issues.append(cmt_iss)

    
    os.makedirs('../data/PRTiger/v5/', exist_ok=True)

    # pd.DataFrame({
    #     'text': only_commits,
    #     'title': title_list
    # }).to_csv('../data/PRTiger/v3/only_commits.csv')

    pd.DataFrame({
        'text': cmt_issues,
        'title': title_list
    }).to_csv('../data/PRTiger/v5/commits-issue-tkn.csv')

    # pd.DataFrame({
    #     'text': enhanced_bodies,
    #     'title': title_list
    # }).to_csv('../data/PRTiger/v2/tok_all.csv')

    # pd.DataFrame({
    #     'text': html_bodies,
    #     'title': title_list
    # }).to_csv('../data/PRTiger/v1/test_all.csv')


def complement_checklist(s):
    s1 = re.sub('^- \[\s*\]', '- [x]', s)
    if s1 != s:
        return s1
    s2 = re.sub('^\* \[\s*\]', '\* [x]', s)
    return s2


def is_checklist(s):
    if re.findall('^- \[.*\]', s):
        return True
    if re.findall('^\* \[.*\]', s):
        return True
    if re.findall('^\[.*\]', s):
        return True
    if re.findall('^\[.*\]', s):
        return True
    return False


def remove_useless_info(s):
    # remove cc @xxx
    s = re.sub('cc @.*', '', s)
    
    # remove html
    s = re.sub(r'https?:\/\/.*[\r\n]*', '', s)

    return s


def export_text_data_no_template(ver_num):
    """
    we handle the pure text body here
    """

    title_list = list()
    count = 0
    improper_titles = 0
    found_title_in_body = 0
    enhanced_bodies = list()
    
    for dir in tqdm(os.listdir(pr_folder)):
        cur_temp = ''

        # save the template sentences
        if os.path.exists('../data/PR-templates/{}.json'.format(dir)):
            with open('../data/PR-templates/{}.json'.format(dir)) as f:
                cur_json = ujson.load(f)

            tmp_cnt = len(cur_json['data']["repository"]["pullRequestTemplates"])

            for i in range(tmp_cnt):
                if cur_json['data']["repository"]["pullRequestTemplates"][i]["filename"].lower() in template_names:
                    body = cur_json['data']["repository"]["pullRequestTemplates"][i]['body']
                    sents = body.splitlines()

                    sent_list = list()

                    for sent in sents:
                        if len(sent.strip()) > 0:

                            str_sent = sent.strip().lower()
                            # remove annotations
                            if re.findall('^<!--', str_sent):
                                continue

                            cklist = re.findall('^- \[.*\] (.*)', str_sent)
                            if len(cklist) > 0:
                                sent_list.append(cklist[0])
                                continue

                            cklist = re.findall('^\* \[.*\] (.*)', str_sent)
                            if len(cklist) > 0:
                                sent_list.append(cklist[0])
                                continue

                            cklist = re.findall('^\[.*\] (.*)', str_sent)
                            if len(cklist) > 0:
                                sent_list.append(cklist[0])
                                continue

                            cklist = re.findall('^\[.*\] (.*)', str_sent)
                            if len(cklist) > 0:
                                sent_list.append(cklist[0])
                                continue

                            sent_list.append(str_sent)

            cur_temp = ' '.join(sent_list)
            cur_temp = cur_temp.encode("ascii", "ignore")
            cur_temp = cur_temp.decode()


        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)

            improved_title = improve_title(cur_pr['title'])
            
            if rule1checker(improved_title) or rule2checker(improved_title):
                improper_titles += 1
                os.unlink(pr_folder + dir + '/' + json_file)
                continue
            
            count += 1

            cleaned_body_text = cur_pr['bodyText'].encode("ascii", "ignore")
            cur_body = cleaned_body_text.decode()
            body_sents = cur_body.splitlines()
            
            enhanced_body = ''

            body_text = list()

            for sent in body_sents:
                if len(sent.strip()) == 0:
                    continue

                sent = sent.strip().lower()

                if len(cur_temp) > 0:
                    try:
                        cur_temp.index(sent)
                        continue
                    except ValueError:
                        if is_checklist(sent):
                            continue
                        body_text.append(sent)
                else:
                    if is_checklist(sent):
                        continue

                    body_text.append(sent)

            if len(body_text) == 0:
                continue

            real_body = list()

            for sent in body_text:
                if len(sent.strip()) == 0:
                    continue

                sent_low = sent.strip().lower()

                if re.findall('^(signed-off-by|co-authored-by|also-by):', sent_low):
                    continue

                if is_checklist(sent_low):
                    continue
                
                sent_low = remove_useless_info(sent_low)

                real_body.append(sent_low)
            
            body_txt = ' '.join(real_body)

            body_txt = re.sub('\`', '', body_txt)

            if len(body_txt.strip()) > 0:
                cur_body = body_txt.strip()
                enhanced_body = START_DESCRIPTION + ' ' + body_txt.strip() + ' ' + END_DESCRIPTION

            # 2. add commits
            count_commits = cur_pr['commits']['totalCount']

            # check commits
            if count_commits > 0:
                for i in range(min(count_commits, 30)):
                    if len(cur_pr['commits']['edges'][i]) > 0:
                        commit_msg = cur_pr['commits']['edges'][i]['node']['commit']['message']

                        if len(commit_msg) > 0:
                            # cleaned_commit = emoji_pattern.sub(r'', commit_msg)
                            # ignore non-ascii chars

                            cleaned_commit = commit_msg.encode("ascii", "ignore")
                            cleaned_commit = cleaned_commit.decode()

                            for cmt_line in cleaned_commit.splitlines():
                                
                                cmt_line = cmt_line.strip()

                                if len(cmt_line) == 0:
                                    continue

                                cmt_line = cmt_line.lower()

                                if re.findall(r'^(signed-off-by|co-authored-by|also-by):', cmt_line):
                                    continue

                                # if re.findall(r'^\* .*', cmt_line):
                                #     continue

                                if re.findall(r'^merge .*? branch .*? into', cmt_line):
                                    continue

                                if re.findall(r'^merge branch .*? into', cmt_line):
                                    continue

                                if re.findall(r'^merge pull request \#', cmt_line):
                                    continue

                                if re.findall(r'^merge branch \'', cmt_line):
                                    continue

                                cmt_line = remove_useless_info(cmt_line)
                                cmt_line = re.sub(r'\`\`\` .* \`\`\`', '', cmt_line)
                                cmt_line = re.sub('\`', '', cmt_line)

                                cur_body += ' ' + cmt_line
                                enhanced_body += ' ' + START_COMMIT + ' ' + cmt_line.strip() + ' ' + END_COMMIT

            # check issues
            issues = cur_pr['closingIssuesReferences']

            if len(issues['edges']) > 0:
                for i in range(len(issues['edges'])):
                    if len(cur_pr['closingIssuesReferences']['edges'][i]['node']['title'] + \
                        cur_pr['closingIssuesReferences']['edges'][i]['node']['bodyText']) > 0:
                        issue_title = cur_pr['closingIssuesReferences']['edges'][i]['node']['title']

                        cleaned_title = issue_title.encode("ascii", "ignore")
                        cleaned_title = cleaned_title.decode().strip()

                        if len(cleaned_title) == 0:
                            continue

                        cleaned_title = cleaned_title.lower()

                        cur_body += " " + cleaned_title
                        enhanced_body += ' ' + START_ISSUE + ' ' + cleaned_title + ' ' + END_ISSUE

                        # to_add.append(START_ISSUE + ' ' + cleaned_title.strip() + ' ' + END_ISSUE)
                        # enhanced_body += ' ' + cleaned_title.strip()
                        # cur_body += " " + cur_pr['closingIssuesReferences']['edges'][i]['node']['bodyText']

            body_tokenize = nltk.word_tokenize(cur_body)
            # removing punctuation
            body_words  = [x.lower() for x in body_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]
            title_tokenize = nltk.word_tokenize(improved_title)
            # removing punctuation
            title_words = [x.lower() for x in title_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]

            if rule3checker(title_words, body_words):
                improper_titles += 1
                continue

            # if len(body_words) < 30:
            #     # os.unlink(pr_folder + dir + '/' + json_file)
            #     improper_body_length += 1
            #     continue

            # if len(body_words) > 1000:
            #     # os.unlink(pr_folder + dir + '/' + json_file)
            #     improper_body_length += 1
            #     continue

            try:
                cur_body.index(improved_title.lower())
                improper_titles += 1
                found_title_in_body += 1
                continue
            except ValueError:
                title_list.append(improved_title.lower())
                enhanced_bodies.append(enhanced_body.strip().lower())

    os.makedirs('../data/PRTiger/v{}/'.format(ver_num), exist_ok=True)

    pd.DataFrame({
        'text': enhanced_bodies,
        'title': title_list
    }).to_csv('../data/PRTiger/v{}/no-template.csv'.format(ver_num))
    # logging.info('the # of improper body length: {}'.format(improper_body_length))
    logging.info('the # of improper titles: {}'.format(improper_titles))
    logging.info('found title in body: {}'.format(found_title_in_body))


def remove_empty_folder():
    """
    After filtering, we have 34 empty folders
    """

    root = pr_folder
    folders = list(os.walk(root))[1:]
    removed = 0
    left = 0
    for folder in folders:
        if not folder[2]:
            # print(folder[0])
            os.rmdir(folder[0])
            removed += 1
        else:
            left += 1

    print('the # of removed is: {}'.format(removed))
    print('the # of left folders is: {}'.format(left))


def export_title():
    titles = {}
    have_issues = 0
    total_prs = 0

    for dir in os.listdir(pr_folder):
        logging.info(dir)

        for json_file in os.listdir(pr_folder + dir):
            with open(pr_folder + dir + '/' + json_file) as f:
                cur_pr = ujson.load(f)

            improved_title = improve_title(cur_pr['title'])
            
            if rule1checker(improved_title) or rule2checker(improved_title):
                continue

            total_prs += 1
            issues = cur_pr['closingIssuesReferences']
            if len(issues['edges']) > 0:
                have_issues += len(issues['edges'])

            if improved_title in titles:
                titles[improved_title] += 1
            else:
                titles[improved_title] = 1
    
    import collections
    od = collections.OrderedDict(sorted(titles.items()))
    with open('title_key.txt', 'w') as f:
        for k, v in od.items(): 
            f.write(k)
            f.write(' ')
            f.write(str(v))
            f.write('\n')

    print('# of total PRs {}'.format(total_prs))
    print('# of PRs have issues is {}'.format(have_issues))


if __name__ == '__main__':
    init_logger('../log/29-Mar-clean_data.log')
    # filter_unmerged_issues()
    # filter_future_commits()
    # filter_improper_commit_length()
    # filter_non_ascii()
    # filter_bot_written()
    # count_associated_issues()
    # count_empty_body()
    # export_raw_data()
    remove_empty_folder()

    # parser = argparse.ArgumentParser(description='pass the ver num')
    # parser.add_argument('--ver', help='version number', required=True)

    # args = parser.parse_args()

    # ver_num = int(args.ver)
    
    # export_text_data_no_template(ver_num)
    # export_title()
    
    # remove_empty_prs()