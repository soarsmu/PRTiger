"""
Analyze the human evaluation
"""

import pandas as pd
import ast

eval_folder = '../data/human-evaluation/'

# gold, bart, t5

def convert_real_order(eval_file, conv_file):
    eval_df = pd.read_csv(eval_file, index_col=0)
    real_ranks = list()

    ## for rank
    ground_file = '../data/human-evaluation/sampled-ground.csv'
    df = pd.read_csv(ground_file)
    gold_correct, gold_natural, gold_comp = list(), list(), list()
    bart_correct, bart_natural, bart_comp = list(), list(), list()
    t5_correct, t5_natural, t5_comp = list(), list(), list()

    for index, row in df.iterrows():
        s = row['result'][1:-1]
        s = s.replace('}, {', ',')
        cur_map = ast.literal_eval(s)
        keys = list(cur_map.keys())

        num_to_app = dict()
        for i in range(3):
            num_to_app[i] = keys[i]
            cur_map[keys[i]] = i

        row = eval_df.iloc[index]

        gold_correct.append(row[cur_map['gold'] * 3])
        gold_natural.append(row[cur_map['gold'] * 3 + 1])
        gold_comp.append(row[cur_map['gold'] * 3 + 2])

        bart_correct.append(row[cur_map['bart'] * 3])
        bart_natural.append(row[cur_map['bart'] * 3 + 1])
        bart_comp.append(row[cur_map['bart'] * 3 + 2])

        t5_correct.append(row[cur_map['t5'] * 3])
        t5_natural.append(row[cur_map['t5'] * 3 + 1])
        t5_comp.append(row[cur_map['t5'] * 3 + 2])


        rank = eval_df.iloc[index].loc['Rank'].split(',')
        real_rank = list()
        real_rank.append(rank[cur_map['gold']])
        real_rank.append(rank[cur_map['bart']])
        real_rank.append(rank[cur_map['t5']])
        
        real_ranks.append(','.join(real_rank))
    
    pd.DataFrame({
        'gold-correctness': gold_correct,
        'gold-naturalness': gold_natural,
        'gold-comprehensibility': gold_comp,
        'bart-correctness': bart_correct,
        'bart-naturalness': bart_natural,
        'bart-comprehensibility': bart_comp,
        't5-correctness': t5_correct,
        't5-naturalness': t5_natural,
        't5-comprehensibility': t5_comp,
        'rank': real_ranks
    }).to_csv(conv_file, index=False)

if __name__ == "__main__":
    convert_real_order(eval_folder + 'eval-3.csv', eval_folder + 'c_eval_3.csv')