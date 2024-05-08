"""
Computes statistics on the frequency of terms in COHA and their distribution across documents
"""

import argparse
import os
from typing import Tuple, Dict
import pandas as pd
from tqdm import tqdm

import coha_utils


def doc2vocab(file, vocab):
    with open(file, encoding='latin-1') as fp:
        lines = fp.readlines()
        assert len(lines) == 1

    doc_words = lines[0].split()
    doc_vocab = [w for w in doc_words if w in vocab]
    doc_vocab = list(set(doc_vocab))
    return doc_vocab


def load_vocab(glove_dir: str, run_name: str) -> Tuple[Dict[str, int], Dict[int, str]]:
    """
    Loads dictionaries of word-to-index and index-to-word vocabulary conversions.
    :param glove_dir: location of the GloVe trained embeddings
    :param run_name:
    :return:
    """
    with open(f'{glove_dir}/{run_name}vocab.txt', 'r') as f:
        words = [x.rstrip().split(' ')[0] for x in f.readlines()]
    vocab = {w: idx for idx, w in enumerate(words)}
    ivocab = {idx: w for idx, w in enumerate(words)}
    return vocab, ivocab


def main(args):
    # Load documents
    print('[INFO] Loading documents')
    start_year, end_year = args.subset.split('_')
    documents = coha_utils.load_coha_docs_time_subset(
        loc_dir=args.coha_metadata_loc, start_year=start_year, end_year=end_year)
    N = len(documents)

    # Load vocabulary
    print('[INFO] Loading vocabulary')
    vocab, _ = load_vocab(
        glove_dir=os.path.join(args.vocab_base_dir, f'coha_{args.subset}'), run_name='')
    V = len(vocab)

    unique_dict = {word: 0 for word in vocab.keys()}
    for doc_id in tqdm(documents, desc='Computing number of unique docs'):
        try:
            doc_vocab = doc2vocab(
                file=f'{args.coha_individual_path}/coha_{doc_id}.txt', vocab=vocab)
            for w in doc_vocab:
                unique_dict[w] += 1
        except FileNotFoundError:
            continue

    print('[INFO] Computing word frequencies')
    with open(f'{args.vocab_base_dir}/coha_{args.subset}/vocab.txt', 'r') as f:
        freq_dict = {x.rstrip().split(' ')[0]: x.rstrip().split(' ')[1] for x in f.readlines()}

    # Combine into a data frame
    df = pd.DataFrame.from_dict(unique_dict, orient='index').reset_index()
    df.rename(columns={'index': 'word', 0: 'Unique docs'}, inplace=True)
    df['Frequency'] = df['word'].map(freq_dict)
    df['Frequency'] = df['Frequency'].astype(int)

    # Stats
    percent_docs = 0.01
    x = df.loc[df['Unique docs'] <= int(len(documents) * percent_docs)]
    print(f'[INFO] {round(len(x) / len(freq_dict) * 100, 0)}% of terms appear '
          f'in less than {round(percent_docs * 100, 0)}% of documents')

    min_term = 100
    x = df.loc[df['Frequency'] <= min_term]
    print(f'[INFO] {round(len(x) / len(freq_dict) * 100, 0)}% of terms appear '
          f'fewer than {min_term} times')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--coha_individual_path', required=True)
    parser.add_argument('--coha_metadata_loc', required=True)
    parser.add_argument('--vocab_base_dir', required=True)
    parser.add_argument('--subset', required=True, type=str, choices=['1900_1912', '1920_1930', '1800_2010'])

    args = parser.parse_args()
    main(args)
