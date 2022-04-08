"""
find an example which has the highest ROUGE-2 F2 Score in BART
"""
from rouge import Rouge
rouge = Rouge()

predicted_folder = '../predicted/'
with open(predicted_folder + 'title-test-1.txt') as f:
    lines = f.readlines()

barts, t5s, berts, pysums, itapes = [], [], [], [], []

with open(predicted_folder + 'bart.txt') as f:
    barts = f.readlines()

with open(predicted_folder + 't5.txt') as f:
    t5s = f.readlines()

with open(predicted_folder + 'bertsum.txt') as f:
    berts = f.readlines()

with open(predicted_folder + 'prsum.txt') as f:
    prsum = f.readlines()

with open(predicted_folder + 'itape.txt') as f:
    itapes = f.readlines()

found = 0
for i in range(len(lines)):
    bart_score = rouge.get_scores(barts[i].strip(), lines[i].strip())[0]['rouge-2']['f']

    if bart_score <= rouge.get_scores(t5s[i].strip(), lines[i].strip())[0]['rouge-2']['f']:
        continue

    if bart_score <= rouge.get_scores(berts[i].strip(), lines[i].strip())[0]['rouge-2']['f']:
        continue

    if bart_score <= rouge.get_scores(prsum[i].strip(), lines[i].strip())[0]['rouge-2']['f']:
        continue

    if bart_score <= rouge.get_scores(itapes[i].strip(), lines[i].strip())[0]['rouge-2']['f']:
        continue

    print(i + 1)
    found += 1
    if found == 5:
        break