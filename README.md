# Structure
- Data
- Summarization Methods
- Results


## Data
The data is available under [`./data/PRTiger.zip`](./data/PRTiger.zip).
After unzipping the data,
- no-token: files under this sub-folder do not have seperators among description, commit messages, and issues
- with-token: files under this sub-folder contains seperators among different resources in the source sequence

## Summarization Methods
### Fine-tuning BART and T5
- For fine-tuning BART and T5, please use the script under [`./fine-tuning/run_rummarization.py`](./fine-tuning/run_rummarization.py)
- Install the `requirements.txt`

### Oracle Extraction
The script is available `./src/oracle_extractive.py`

### iTAPE
Please refer to [iTAPE Repo](https://github.com/imcsq/iTAPE)

### PRSummarizer
Please refer to [PRSummarizer Repo](https://github.com/Tbabm/PRSummarizer)

### BertSumExt
**Environment**: Dockerfile is presented at BertSumExt/Dockerfile for this BertSumExt

**Changes from Original Code**:
- Set extractive summarizer to return one sentence instead of top 3 sentences

**Training and Evaluation**: Please refer [`here`](https://github.com/happygirlzt/ICSME-PRTiger/blob/main/BertSumExt/README.md)

## Results
### Automatic Evaluation
The generated titles from five approaches and the oracle extraction are located under [`./results/automatic-evaluation`](./results/automatic-evaluation).

### Human Evaluation
The results can be found under `./results/human-evaluation/`.
`c_eval_1.csv`, `c_eval_2.csv`, and `c_eval_3.csv` are the response from our three non-author human evaluators.
`sampled-ground.csv` is the shuffled survey sent to the evaluators.
