#
# Set up the 1900-1912 COHA corpus and the 1920-1930 COHA corpus (used for the Chu Chu analysis in Figure 1)
#

import os
import subprocess
from typing import List
from tqdm import tqdm

import coha_utils
import file_utils


def generate_subset(documents: List[str], out_path: str, individual_path: str):
    # Consolidate documents
    out_file = os.path.join(out_path, 'consolidated.txt')
    os.makedirs(out_path, exist_ok=True)
    os.makedirs(os.path.join(out_path, 'individual_texts'), exist_ok=True)

    # Save consolidated .txt -- this separates documents using a newline, as
    # indicated by GloVe instructions (https://github.com/stanfordnlp/GloVe/tree/master/src)
    for doc_id in tqdm(documents):
        doc_file = f'{individual_path}/coha_{doc_id}.txt'
        # Append to consolidated .txt
        try:
            with open(doc_file, 'r') as dfile:
                doc_text = dfile.read() + '\n'
                mode = 'a' if os.path.exists(out_file) else 'w'
                with open(out_file, mode) as outf:
                    outf.write(doc_text)

            # Save individual file
            os.popen(f'cp {doc_file} {out_path}/individual_texts/coha_{doc_id}.txt')

        except FileNotFoundError:
            print(f'[WARNING] File {doc_id} not found')

    # Run GloVe (to generate co-occurrence matrix and vocab)
    subprocess.call(
        [f"run_glove.sh",
         '',
         f'../GloVe/',
         f'{out_path}/',
         out_file.replace('.txt', ''),
         ''])


def main():
    # Paths
    coha_metadata_dir = f'{str(file_utils.get_root_path())}/data'
    base_out_path = f'{str(file_utils.get_root_path())}/corpora'
    individual_path = f'{str(file_utils.get_root_path())}/data/individual_texts'

    # COHA 1900-1912 (Moore period)
    documents_1900_1912 = coha_utils.load_coha_docs_1900_1912(loc_dir=coha_metadata_dir)
    out_path = f'{base_out_path}/coha_1900_1912'
    generate_subset(
        documents=documents_1900_1912, out_path=out_path, individual_path=individual_path
    )

    # COHA 1920-1929 Including Chu Chu
    docs = coha_utils.load_coha_docs_time_subset(
        loc_dir=coha_metadata_dir, start_year=1920, end_year=1929)
    out_path = f'{base_out_path}/coha_{1920}_{1929}'
    generate_subset(
        documents=docs, out_path=out_path, individual_path=individual_path
    )

    # COHA 1920-1929 Excluding Chu Chu
    docs = coha_utils.load_coha_docs_time_subset(
        loc_dir=coha_metadata_dir, start_year=1920, end_year=1929)
    docs = [d for d in docs if d != '3526']
    out_path = f'{base_out_path}/coha_{1920}_{1929}_excChuChu'
    generate_subset(
        documents=docs, out_path=out_path, individual_path=individual_path
    )


if __name__ == '__main__':
    main()
