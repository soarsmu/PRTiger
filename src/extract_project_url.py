"""
extract top 100 starred projects urls
"""

import re

def extract_url(data_file, generated_file):
    with open(data_file) as f:
        lines = f.readlines()
    
    organizations, repos = list(), list()

    for i in range(7, 107):
        line = lines[i]
        items = line.split('|')
    
        splitted = items[2].strip().split('/')
        print(splitted)

        organizations.append(splitted[-2])
        repos.append(splitted[-1][:-1])

    with open(generated_file, 'w') as f:
        for org, rep in zip(organizations, repos):
            f.write('{}/{}\n'.format(org, rep))

if __name__ == "__main__":
    langs = ['cpp', 'c']
    top_repos = ['../data/repo-list/100_forked.txt', '../data/repo-list/100_java.txt', 
    '../data/repo-list/100_javascript.txt', '../data/repo-list/100_python.txt', 
    '../data/repo-list/100_stared_repos.txt']

    repo_set = set()

    for top_repo in top_repos:
        with open(top_repo) as f:
            lines = f.readlines()
        for line in lines:
            repo_set.add(line.strip())

    for lang in langs:
        data_file = '../data/repo-list/top_100_{}.md'.format(lang)
        generated_file = '../data/repo-list/top_100_{}_repos.txt'.format(lang)
        
        extract_url(data_file=data_file, generated_file=generated_file)

        real_file = '../data/repo-list/100_{}.txt'.format(lang)

        
        real_lines = list()
        with open(generated_file) as f:
            lines = f.readlines()
        for line in lines:
            if not line.strip() in repo_set:
                real_lines.append(line)

        print(len(real_lines))
        with open(real_file, 'w') as f:
            for line in real_lines:
                f.write(line)

    # log_files = ['../log/crawl-22-Feb.log', '../log/crawl-java-22-Feb.log', 
    # '../log/crawl-javascript-22-Feb.log', '../log/crawl-python-22-Feb.log']

    # need_to_crawl_file = ['../data/100_forked.txt', '../data/100_java.txt',
    # '../data/100_javascript.txt', '../data/100_python.txt']

    # left_repo = list()
    # for log_file, crawl_file in zip(log_files, need_to_crawl_file):
    #     done_repos = set()
    #     with open(log_file) as f:
    #         lines = f.readlines()
    #     for line in lines:
    #         found = re.findall('Crawling pull requests from \'(.+/.+)\' is done', line)
    #         if len(found) > 0:
    #             done_repos.add(found[0])

    #     print('finished {}'.format(len(done_repos)))
        
    #     with open(crawl_file) as f:
    #         lines = f.readlines()

    #     for line in lines:
    #         if not line.strip() in done_repos:
    #             print(line)
    #             left_repo.append(line)

    # with open('../data/left.txt', 'w') as f:
    #     for l in left_repo:
    #         f.write(l)