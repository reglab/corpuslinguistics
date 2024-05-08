"""
Computes the bias scores for Figure 1 on the corpus including and excluding the Chu Chu the Horse document
in COHA 1920-1929
"""

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from functools import partial
from multiprocessing import Pool
from typing import Dict
from tqdm import tqdm

import bias_utils
import vector_utils
import coha_utils
from setup import generate_subset
import file_utils


def safe_delete(file: str):
    try:
        os.remove(file)
    except OSError:
        pass


def copy_check(f: str, out_file: str):
    if not os.path.exists(out_file):
        os.system(f'cp {f} {out_file}')


def run_iteration(k: int, vector_loc: str, bias_query: Dict[str, str]):
    # Save in GloVe format and set up files to run GloVe (save vocab and cooccurrence.bin)
    output_dir = Path(vector_loc, str(k))
    safe_delete(f'{output_dir}/vectors.txt')

    output_dir.mkdir(parents=True, exist_ok=True)
    copy_check(f=f'{vector_loc}/cooccurrence.bin', out_file=f'{output_dir}/cooccurrence.bin')
    copy_check(f=f'{vector_loc}/vocab.txt', out_file=f'{output_dir}/vocab.txt')

    # Run GloVe (only steps 3 shuffle and 4 glove)
    subprocess.call(
        [f"run_glove_partial.sh",
         '',
         f'../GloVe/',
         str(output_dir) + '/',
         '',
         str(k),
         ])

    # Load vectors (we use the center vectors)
    _, _, center_vectors = vector_utils.load_fulltxt_vectors(vectors_file=f'{vector_loc}/{k}/vectors.txt')

    # Compute bias score
    bias_score_utils = bias_utils.assemble_vectors(
        vectors=center_vectors, bias_query=bias_query, pre_normalize=False, post_normalize=False, verbose=False)
    bias_score = bias_utils.compute_bias_score(utils_dict=bias_score_utils, function='cosine')

    # Remove trained vectors
    safe_delete(str(output_dir / 'vectors.txt'))
    safe_delete(str(output_dir / 'cooccurrence.bin'))
    safe_delete(str(output_dir / 'cooccurrence.shuf.bin'))
    safe_delete(str(output_dir / 'vocab.txt'))
    shutil.rmtree(str(output_dir))

    return bias_score


def main(args):
    # Set up White-Chu-Otherization bias query (using word lists from Garg et al.)
    query_name = 'PWTW-PC-OW'
    bias_query = {
        'TA': [
            'harris', 'nelson', 'robinson', 'thompson', 'moore', 'wright', 'anderson', 'clark', 'jackson', 'taylor',
            'scott',  'davis', 'allen', 'adams',  'lewis', 'williams', 'jones', 'wilson',  'martin', 'johnson'],
        'TB': ['chu'],
        'A': [
            'devious', 'bizarre', 'venomous', 'erratic', 'barbaric', 'frightening', 'deceitful', 'forceful',
            'deceptive', 'envious', 'greedy', 'hateful', 'contemptible', 'brutal',  'monstrous', 'calculating',
            'cruel', 'intolerant', 'aggressive', 'monstrous']
    }

    # Set up 1920-1929 corpus
    if not os.path.exists(f'{args.vector_dir}/coha_1920_1929_{args.corpus_type}ChuChu/vocab.txt'):
        print(f'[INFO] Building 1920-1929 corpus {args.corpus_type}')
        docs = coha_utils.load_coha_docs_time_subset(
            loc_dir=args.coha_metadata_loc, start_year=1920, end_year=1929)
        if args.corpus_type == 'exc':
            # Remove Chu Chu
            docs = [d for d in docs if d != '3526']
        out_path = f'{args.vector_dir}/coha_1920_1929_{args.corpus_type}ChuChu'
        generate_subset(
            documents=docs, out_path=out_path, individual_path=args.coha_individual_path)

    # Set up save location
    dict_outfile = os.path.join(args.output_dir, f'chuchu_dict_{args.corpus_type}.json')
    if os.path.exists(dict_outfile):
        with open(dict_outfile, 'r') as f:
            simulation_dict = json.load(f)
        K = args.K - len(simulation_dict[args.corpus_type])
    else:
        simulation_dict = {args.corpus_type: []}
        K = args.K

    if len(simulation_dict[args.corpus_type]) >= args.K:
        return
    print(f'[INFO] Running bootstrap for corpus: {args.corpus_type}')

    bias_scores = []
    with Pool(processes=args.num_processes) as p:
        for i, results in tqdm(
                enumerate(
                    p.imap_unordered(
                        partial(
                            run_iteration,
                            bias_query=bias_query,
                            vector_loc=f'{args.vector_dir}/coha_1920_1929_{args.corpus_type}ChuChu'
                        ),
                        list(range(K)),
                        chunksize=1,
                    )
                ),
                total=len(list(range(K))),
                desc=f"Running simulations"
        ):
            bias_scores.append(results)

    # Check again in case another thread has written more samples during training
    if os.path.exists(dict_outfile):
        with open(dict_outfile, 'r') as f:
            simulation_dict_current = json.load(f)
    else:
        simulation_dict_current = {args.corpus_type: []}
    simulation_dict_current[args.corpus_type].extend(bias_scores)
    with open(dict_outfile, 'w') as f:
        json.dump(simulation_dict_current, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--K', required=False, type=int, default=100)
    parser.add_argument('--num_processes', required=False, type=int, default=4)

    parser.add_argument('--coha_individual_path', required=True)
    parser.add_argument('--coha_metadata_loc', required=True)
    parser.add_argument('--vector_dir', required=True)
    parser.add_argument('--output_dir', required=False)
    parser.add_argument('--corpus_type', type=str, required=True, choices=['inc', 'exc'])

    args = parser.parse_args()

    args.output_dir = str(file_utils.get_root_path() / 'outputs' / 'ChuChu')
    os.makedirs(args.output_dir, exist_ok=True)

    main(args)
