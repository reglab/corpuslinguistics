import numpy as np


def assemble_vectors(vectors: dict, bias_query: dict, pre_normalize: bool,
                     post_normalize: bool = True) -> dict:
    """

    :param vectors: (dict) of unnormalized GloVe vectors
    :param bias_query: (dict) of word lists for each part of the bias query (Targets, Attributes)
    :param pre_normalize: (bool) whether to normalize the attribute vectors
    :param post_normalize: (bool) whether to normalize the surname means
    :return: (dict of np.arrays) All vectors are shape (x, d)
    """
    # Get dimensionality
    d = len(vectors[list(vectors.keys())[0]])

    bias_score_utils = {}

    # Effective word list size (depending on whether words are in the vocab
    sizes = {}
    for word_set in bias_query.keys():
        size = 0
        for w in bias_query[word_set]:
            if w in vectors.keys():
                size += 1
        sizes[word_set] = size

    # Define shapes
    for word_set in bias_query.keys():
        bias_score_utils[word_set] = np.zeros((sizes[word_set], d))
        bias_score_utils[f'{word_set}_list'] = []

    # Populate (un-normalized vectors)
    for word_set in bias_query.keys():
        i = 0
        for w in bias_query[word_set]:
            if w in vectors.keys():
                bias_score_utils[word_set][i, :] = vectors[w]
                bias_score_utils[f'{word_set}_list'].append(w)
                i += 1

    # Normalize
    if pre_normalize:
        for word_set in bias_query.keys():
            normalized_vecs = bias_score_utils[word_set] / np.linalg.norm(bias_score_utils[word_set], axis=1).reshape(-1, 1)
            bias_score_utils[word_set] = normalized_vecs

    # Mean vectors
    MA = np.mean(bias_score_utils['TA'] / np.linalg.norm(bias_score_utils['TA'], axis=1).reshape(-1, 1), axis=0).reshape(1, -1)
    MB = np.mean(bias_score_utils['TB'] / np.linalg.norm(bias_score_utils['TB'], axis=1).reshape(-1, 1), axis=0).reshape(1, -1)

    if post_normalize:
        MA /= np.linalg.norm(MA, axis=1)
        MB /= np.linalg.norm(MB, axis=1)

    bias_score_utils['MA'] = MA
    bias_score_utils['MB'] = MB

    return bias_score_utils


def compute_bias_score(utils_dict: dict, function: str) -> float:
    """
    Compute the cosine bias score for a query.
    :param utils_dict: (dict) including the attribute and target sets
    :param function: (str) the type of bias function: [cosine]
    :return: bias score
    """
    score = None

    if function == 'cosine':
        # mean_i cos(vi, MB) - mean_i cos(vi, MA)
        cB = np.matmul(utils_dict['A'], utils_dict['MB'].T)
        cB /= np.linalg.norm(utils_dict['A'], axis=1).reshape(-1, 1)
        cB /= np.linalg.norm(utils_dict['MB'])

        cA = np.matmul(utils_dict['A'], utils_dict['MA'].T)
        cA /= np.linalg.norm(utils_dict['A'], axis=1).reshape(-1, 1)
        cA /= np.linalg.norm(utils_dict['MA'])
        score = np.mean(cB) - np.mean(cA)
    else:
        raise Exception('[ERROR] Check bias function')

    return score

