from datasets import load_metric
import argparse
from rouge import Rouge

def use_datasets(generated_summaries, reference_summaries):
    metric = load_metric("rouge", seed=42)
    
    result = metric.compute(predictions=generated_summaries, references=reference_summaries, use_stemmer=True)

    # result = metric.compute(predictions=['add http server for frontend and snapshots'], references=['use http server instead of interception'])

    # Extract a few results from ROUGE
    precisions = {key: value.mid.precision * 100 for key, value in result.items()}
    precisions = {k: round(v, 2) for k, v in precisions.items()}
    print("precision")
    print(precisions)

    recalls = {key: value.mid.recall * 100 for key, value in result.items()}
    recalls = {k: round(v, 2) for k, v in recalls.items()}

    print("recall")
    print(recalls)

    fmeasures = {key: value.mid.fmeasure * 100 for key, value in result.items()}
    fmeasures = {k: round(v, 2) for k, v in fmeasures.items()}
    print("f1")
    print(fmeasures)

def use_rouge(generated_summaries, reference_summaries):
    rouge = Rouge()
    scores = rouge.get_scores(generated_summaries, reference_summaries, avg=True)
    print(scores)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='pass the files')
    parser.add_argument('--target', help='target file name')
    parser.add_argument('--predict', help='predicted file name')

    args = parser.parse_args()

    generated_summaries = []
    reference_summaries = []

    with open(args.predict) as f:
        lines = f.readlines()
    for line in lines:
        # generated_summaries.append([word for word in line.strip().split() if not word in stop_words])
        generated_summaries.append(line)

    with open(args.target) as f:
        lines = f.readlines()
    for line in lines:
        # reference_summaries.append([word for word in line.strip().split() if not word in stop_words])
        reference_summaries.append(line)

    # print('using rouge..')
    # use_rouge(generated_summaries, reference_summaries)
    print('using datasets...')
    use_datasets(generated_summaries, reference_summaries)