"""
Generates Figure 1, in which we compare Chu bias scores including and excluding
the document Chu Chu by Francis Bret Harte in COHA 1920-1930.
"""
from typing import Dict, List
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np

import file_utils


def parse_bootstrap_output(
        bootstrap_stats: List[float],
        conf_level: float = 0.95
) -> Dict[str, List[float]]:
    assert conf_level < 1, '[ERROR] Confidence level must be between 0 and 1'

    if len(bootstrap_stats) == 0:
        bootstrap_dict = {
            'mean': 0,
            'median': 0,
            'variance': 0,
            'sd': 0,
            'lower': 0,
            'upper': 0,
            'counts': []
        }
    else:
        bootstrap_stats = np.sort(bootstrap_stats)
        bounds = np.nanpercentile(
            a=bootstrap_stats,
            q=(
                (1 - conf_level) / 2 * 100,
                (conf_level + (1 - conf_level) / 2) * 100
            )
        )
        bootstrap_dict = {
            'mean': np.mean(bootstrap_stats),
            'median': np.median(bootstrap_stats),
            'variance': np.var(bootstrap_stats),
            'sd': np.std(bootstrap_stats),
            'lower': bounds[0],
            'upper': bounds[1],
            'counts': bootstrap_stats
        }
    return bootstrap_dict


def main():
    simulation_dict = {}
    with open(f'{str(file_utils.get_root_path())}/outputs/ChuChu/chuchu_dict_inc.json', 'r') as f:
        simulation_dict_inc = json.load(f)

    with open(f'{str(file_utils.get_root_path())}/outputs/ChuChu/chuchu_dict_exc.json', 'r') as f:
        simulation_dict_exc = json.load(f)

    simulation_dict['inc'] = simulation_dict_inc['inc']
    simulation_dict['exc'] = simulation_dict_exc['exc']

    for corpus_type in ['inc', 'exc']:
        simulation_dict[corpus_type] = [l for l in simulation_dict[corpus_type] if l is not None]

    conf_level = 0.95
    sim_df = pd.DataFrame()
    for corpus, corpus_stats in simulation_dict.items():
        parsed_stats = parse_bootstrap_output(bootstrap_stats=corpus_stats, conf_level=conf_level)
        parsed_stats['corpus'] = corpus
        parsed_stats = {k: [v] for k, v in parsed_stats.items()}
        sim_df = pd.concat([sim_df, pd.DataFrame.from_dict(parsed_stats)])

    sim_df['corpus'] = sim_df['corpus'].map(
        {'inc': 'COHA 1920s\nincluding\n"Chu Chu"', 'exc': 'COHA 1920s\nexcluding\n"Chu Chu"'})

    # Plot
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.axvline(x=0, color='black')
    ax.errorbar(
        ls='none',
        y=sim_df['corpus'], x=sim_df['mean'],
        xerr=(
            np.abs(sim_df['lower'] - sim_df['mean']),
            np.abs(sim_df['upper'] - sim_df['mean'])), zorder=0)
    plt.scatter(y=sim_df['corpus'], x=sim_df['mean'],  zorder=5)
    ax.set_xlabel('Cosine bias score\n'
                  r'Chu surname closer to Otherization words $\longrightarrow$', fontsize=8)
    ax.set(ylabel='')
    ax.set_ylim(-0.5, 1.5)
    plt.tick_params(labelsize=8)
    plt.legend(frameon=False, loc='lower right')
    plt.gca().invert_yaxis()
    fig.tight_layout()
    plt.savefig(
        f'{str(file_utils.get_root_path())}/outputs/ChuChu/bias_scores_{conf_level}.png',
        dpi=400)


if __name__ == '__main__':
    main()
