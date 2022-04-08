import os
import json
import requests
import logging
import sys
sys.path.append("./")
from logger import init_logger
init_logger('../log/crawl-4-Mar.log')

from tqdm import tqdm

# The authz token is a temporary personal access token for testing

HEADERS = {"Authorization": "bearer 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"}


file_names = [
    '../data/repo-list/100_stared_repos.txt',  \
    '../data/repo-list/100_forked.txt',  \
    '../data/repo-list/100_java.txt',   \
    '../data/repo-list/100_javascript.txt', \
    '../data/repo-list/100_python.txt',  \
    '../data/repo-list/100_c.txt', \
    '../data/repo-list/100_cpp.txt'
]

saved_repos = set()

for file in os.listdir('../data/pull-request'):
    saved_repos.add(file)

print('saved {}'.format(len(saved_repos)))


owner_repo_set = set()
for file_name in file_names:
    with open(file_name) as f:
        lines = f.readlines()

    for line in lines:
        owner, repo = line.strip().split('/')

        if not '{}-{}'.format(owner, repo) in saved_repos:
            continue

        owner_repo_set.add(line)

print('the number of owner repo: {}'.format(len(owner_repo_set)))


query_template = """
{
    repository(owner: "%s", name: "%s") {
        pullRequestTemplates {
            body
            filename
        }
    }
}
"""

def crawl(repo_owner: str, name: str, output_directory: str) -> str:
    query = query_template % (repo_owner, name)

    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=HEADERS)
    
    if request.status_code == 200:
        result = request.json()
    else:
        result = None

    try:
        if result and len(result['data']['repository']['pullRequestTemplates']) > 0:
            output_name = output_directory + "{}-{}.json".format(owner, repo)

            with open(output_name, "w") as f:
                f.write(json.dumps(result))
    except TypeError:
        logging.ino('-----' * 10)
        logging.info('did not find')
        logging.info("{}-{}".format(owner, repo))
    
    # edges = result['data']['repository']['pullRequestTemplates']['body']

if __name__ == '__main__':
    for owner_repo in tqdm(owner_repo_set):
        owner, repo = owner_repo.strip().split('/')
        output_dir = '../data/PR-templates/'
        os.makedirs(output_dir, exist_ok=True)

        crawl(owner, repo, output_dir)
        logging.info("Crawling pull request template from '%s/%s' is done" % (owner, repo))