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

Example commands:
- T5
```
CUDA_VISIBLE_DEVICES=2,3,4 python run_summarization.py \
    --model_name_or_path t5-small \
    --do_train \
	--do_eval \
    --do_predict \
    --train_file '../data/PRTiger/v25/train.csv' \
    --validation_file '../data/PRTiger/v25/valid.csv' \
    --test_file '../data/PRTiger/v25/test.csv' \
    --source_prefix "summarize: " \
    --text_column 'text' \
	--summary_column 'summary' \
    --output_dir ./tmp/T5-v25 \
    --per_device_train_batch_size=8 \
    --per_device_eval_batch_size=8 \
    --predict_with_generate
```

- BART
```
CUDA_VISIBLE_DEVICES=2,3,4 python run_summarization.py \
    --model_name_or_path facebook/bart-base \
    --do_train \
	--do_eval \
    --do_predict \
    --train_file '../data/PRTiger/v2/train.csv' \
    --validation_file '../data/PRTiger/v2/valid.csv' \
    --test_file '../data/PRTiger/v2/test.csv' \
    --text_column 'text' \
	--summary_column 'summary' \
    --output_dir ./tmp/v2 \
    --per_device_train_batch_size=8 \
    --per_device_eval_batch_size=8 \
    --predict_with_generate
```

### Oracle Extraction
The script is available [`./src/oracle_extractive.py`](./src/oracle_extractive.py)

### iTAPE
Please refer to [iTAPE Repo](https://github.com/imcsq/iTAPE)

### PRSummarizer
Please refer to [PRSummarizer Repo](https://github.com/Tbabm/PRSummarizer)

### BertSumExt
- **Environment**: Dockerfile is presented at [./BertSumExt/Dockerfile](./BertSumExt/Dockerfile) for this BertSumExt

- **Changes from Original Code**:
    + Set extractive summarizer to return one sentence instead of top 3 sentences

- **Training and Evaluation**: Please refer [`here`](https://github.com/happygirlzt/ICSME-PRTiger/blob/main/BertSumExt/README.md)

## Results
### Automatic Evaluation
The generated titles from five approaches and the oracle extraction are located under [`./results/automatic-evaluation`](./results/automatic-evaluation).

### Human Evaluation
The results can be found under [`./results/human-evaluation/`](`./results/human-evaluation/`).

- `c_eval_1.csv`, `c_eval_2.csv`, and `c_eval_3.csv` are the response from our three non-author human evaluators.

- `sampled-ground.csv` is the shuffled survey sent to the evaluators.

# Citation
If you find this repo useful, please consider to cite our work.

```
@inproceedings{zhang2022automatic,
	author = {Ting Zhang and Ivana Clairine Irsan and Ferdian Thung and DongGyun Han and David Lo and Lingxiao Jiang},
	booktitle = {2022 IEEE International Conference on Software Maintenance and Evolution (ICSME)},
	title = {Automatic Pull Request Title Generation},
	year = {2022},
	volume = {},
	issn = {},
	pages = {71-81},
	doi = {10.1109/ICSME55016.2022.00015},
	url = {https://doi.ieeecomputersociety.org/10.1109/ICSME55016.2022.00015},
	publisher = {IEEE Computer Society},
	address = {Los Alamitos, CA, USA},
	month = {oct}
}
```
