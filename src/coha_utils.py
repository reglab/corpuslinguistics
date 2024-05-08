from typing import List
import glob
import json
import pandas as pd


def load_coha_period_docs(
        start_year: int, end_year: int, individual_path: str, metadata_path: str) -> List[str]:
    """
    Returns a list of files pointing to COHA documents belonging to the period defined
    by the start and end year (inclusive)
    :param metadata_path: Location of the COHA metadata json
    :param individual_path: Location of the individual, pre-processed COHA documents
    :param start_year:
    :param end_year:
    :return:
    """
    all_docs = glob.glob(f'{individual_path}/*.txt')

    # Get decade document subset
    doc_metadata = load_coha_metadata(loc_dir=metadata_path)

    # Subset
    run_years = list(range(start_year, end_year + 1))
    decade_metadata = doc_metadata.loc[doc_metadata['year'].astype(int).isin(run_years)].copy()
    decade_idxs = decade_metadata.index.tolist()

    decade_docs = [doc for doc in all_docs if doc.split('/')[-1].replace('coha_', '').replace('.txt', '') in decade_idxs]

    return decade_docs


def load_coha_metadata(loc_dir: str) -> pd.DataFrame:
    with open(f'{loc_dir}/coha_document_metadata.json', ) as f:
        doc_metadata = json.load(f)
    doc_metadata = pd.DataFrame.from_dict(doc_metadata, orient='index')
    return doc_metadata


def load_coha_docs_time_subset(loc_dir: str, start_year: int, end_year: int) -> List[str]:
    """
    Returns document ids for COHA documents within a given time period
    :param loc_dir: Location of the metadata JSON
    :param start_year:
    :param end_year: inclusive
    :return:
    """
    # Ensure we have ints for the years
    start_year = int(start_year)
    end_year = int(end_year)

    # Load COHA metadata
    metadata = load_coha_metadata(loc_dir=loc_dir)

    # Subset to time period
    subset_doc_df = metadata.copy()
    subset_doc_df = subset_doc_df.loc[subset_doc_df['year'].isin(range(start_year, end_year + 1))]
    subset_doc_df['doc_id'] = subset_doc_df.index
    return list(subset_doc_df['doc_id'].unique())


def load_coha_docs_1900_1912(loc_dir: str) -> List[str]:
    """
    Returns document ids for COHA documents from 1900 to 1912.
    :param loc_dir: Location of the metadata JSON
    :return:
    """
    docs = load_coha_docs_time_subset(loc_dir=loc_dir, start_year=1900, end_year=1912)
    return docs
