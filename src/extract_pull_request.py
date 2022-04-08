"""
Extracl PR from the crawled cursors
"""

import os
import json
import logging


def extract_edges(content: str):
    j = json.loads(content)
    return j['data']['repository']['pullRequests']['edges']


def save_nodes(output_dir: str, edges: list):
    for edge in edges:
        node = edge['node']
        with open('%s/%s.json' % (output_dir, node['number']), "w") as output:
            output.write(json.dumps(node))

if __name__ == '__main__':
    need_to_crawl_file = [
        '../data/repo-list/100_forked.txt', 
        '../data/repo-list/100_java.txt',
        '../data/repo-list/100_javascript.txt', 
        '../data/repo-list/100_python.txt', 
        '../data/repo-list/100_stared_repos.txt',
        '../data/repo-list/100_c.txt', 
        '../data/repo-list/100_cpp.txt'
    ]

    for need_file in need_to_crawl_file:
        with open(need_file) as f:
            lines = f.readlines()

        owner_repo_set = set()
        for line in lines:
            owner_repo_set.add(line)

        for owner_repo in owner_repo_set:
            owner, repo = owner_repo.strip().split('/')
            output_dir = '../data/pull-request/%s-%s/' % (owner, repo)

            if not os.path.exists('../data/PR/%s-%s/' % (owner, repo)):
                print(owner_repo)
                continue

            if os.path.exists(output_dir):
                continue

            print(output_dir)
            os.makedirs(output_dir, exist_ok=True)

            with open('../data/PR/%s-%s/first.json' % (owner, repo)) as f:
                content = f.read()
                edges = extract_edges(content)
                save_nodes(output_dir, edges)
                last_cursor = edges[0]['cursor']

            while last_cursor:
                print(last_cursor)
                try:
                    with open("../data/PR/%s-%s/%s" % (owner, repo, last_cursor)) as f:
                        content = f.read()
                        edges = extract_edges(content)
                        save_nodes(output_dir, edges)
                        last_cursor = edges[0]['cursor']
                except Exception as e:
                    logging.debug(e, exc_info=True)
                    last_cursor = None
                    continue