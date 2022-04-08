import os
import json
import requests
import logging
import sys
sys.path.append("./")
from logger import init_logger
from tqdm import tqdm
import argparse

# The authz token is a temporary personal access token for testing

HEADERS = {"Authorization": "bearer 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"}


query_template = """
{
    repository(owner: "%s", name: "%s") {
        pullRequests(last: %s %s) {
            edges {
                cursor
                node {
                    number
                    closingIssuesReferences(first: 30) {
                        edges {
                            node {
                                number
                                title
                                body
                                bodyText
                                bodyHTML
                            }
                        }
                    }
                    title
                    body
                    bodyText
                    bodyHTML
                    commits(first: 30) {
                        totalCount
                        edges {
                        node{
                            commit {
                                message
                                committedDate                            
                            }
                        }
                        }
                    }
                    author {
                        login
                        __typename
                    }
                    closed
                    merged
                    state
                    publishedAt
                    updatedAt
                }
            }
        }
    }
    
    rateLimit {
        limit
        cost
        remaining
        resetAt
    }
}
"""


def run_query(q: str) -> dict:
    request = requests.post('https://api.github.com/graphql', json={'query': q}, headers=HEADERS)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, q))


def generate_query(repo_owner: str, name: str, issues_before_cursor: str = None, num_issues: int = 50) -> str:
    before_cursor = ', before: "%s"' % issues_before_cursor if issues_before_cursor else ""
    try:
        q = query_template % (repo_owner, name, str(num_issues), before_cursor)
    except Exception as e:
        logging.error("Query failed", e, exc_info=True)
        # return with smaller number of issues
        return generate_query(repo_owner, name, issues_before_cursor, num_issues - 10)
    return q


def crawl(repo_owner: str, name: str, output_directory: str,
        issues_before_cursor: str = None, num_issues: int = 50) -> str:
    query = generate_query(repo_owner, name, issues_before_cursor, num_issues)
    try:
        result = run_query(query)
    except Exception as e:
        logging.error("Query failed", e, exc_info=True)
        return crawl(repo_owner, name, output_directory, issues_before_cursor, num_issues-20)
    new_cursor = None

    output_name = output_directory + issues_before_cursor \
        if issues_before_cursor else output_directory + "first.json"
    with open(output_name, "w") as f:
        f.write(json.dumps(result))
    
    try:
        edges = result['data']['repository']['pullRequests']['edges']
    except TypeError:
        return None
    if len(edges) == num_issues:
        new_cursor = edges[0]['cursor']
        logging.info("Next cursor: %s" % new_cursor)

    remaining_rate_limit = result["data"]["rateLimit"]["remaining"]  # Drill down the dictionary
    logging.info("Remaining rate limit - {}".format(remaining_rate_limit))

    return new_cursor


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pass the lang')
    parser.add_argument('--lang', help='language name')

    args = parser.parse_args()
    init_logger('../log/crawl-{}-2-Mar.log'.format(args.lang))

    with open('../data/repo-list/100_{}.txt'.format(args.lang)) as f:
        lines = f.readlines()

    owner_repo_set = set()
    for line in lines:
        owner_repo_set.add(line)

    for owner_repo in tqdm(owner_repo_set):
        owner, repo = owner_repo.strip().split('/')
        output_dir = '../data/PR/%s-%s/' % (owner, repo)

        if os.path.exists(output_dir):
            continue

        logging.info(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        cursor = crawl(owner, repo, output_dir, None)
        while cursor:
            cursor = crawl(owner, repo, output_dir, cursor)
        logging.info("Crawling pull requests from '%s/%s' is done" % (owner, repo))