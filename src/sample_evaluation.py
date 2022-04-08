"""
we sample 150 PRs for human evaluation
"""

import pandas as pd
import random
random.seed(42)

if __name__ == '__main__':
    n = 150

    test_csv = '/home/zhaozheng/generating-bug-report-titles/data/PRTiger/v25/test.csv'

    df = pd.read_csv(test_csv)

    sources, titles = df['text'].tolist(), df['summary'].tolist()
    indexes = list(range(len(sources)))

    sampled = random.sample(indexes, n)
    
    with open('sampled_index.txt', 'w') as f:
        for index in sampled:
            f.write(str(index) + '\n')
    
    with open('../predicted/t5.txt') as f:
        t5_lines = f.readlines()

    with open('../predicted/bart.txt') as f:
        bart_lines = f.readlines()

    sampled_source, sampled_gold = list(), list()
    titles_1, titles_2, titles_3 = list(), list(), list()

    for index in sampled:
        sampled_source.append(sources[index])
        three_titles = [{'bart': bart_lines[index].strip()}, {'t5': t5_lines[index].strip()}, {'gold': titles[index].strip()}]

        random.shuffle(three_titles)
        sampled_gold.append(three_titles)

        print(three_titles)
        titles_1.append(list(three_titles[0].values())[0])
        titles_2.append(list(three_titles[1].values())[0])
        titles_3.append(list(three_titles[2].values())[0])
        
        # title_1.append(three_titles[0])
        # title_2.append(three_titles[1])
        # title_3.append(three_titles[2])

        # sampled_bart.append(bart_lines[index])
        # sampled_t5.append(t5_lines[index])
        # sampled_gold.append(titles[index])

    pd.DataFrame({
        'source': sampled_source,
        'result': sampled_gold}).to_csv('sampled-ground.csv', index=False)

    pd.DataFrame({
        'source': sampled_source,
        'title_1': titles_1,
        'title_2': titles_2,
        'title_3': titles_3}).to_csv('sampled-for-evaluation.csv', index=False)