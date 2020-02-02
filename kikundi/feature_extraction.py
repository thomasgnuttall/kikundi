from collections import OrderedDict
from itertools import combinations
from multiprocessing import Pool
import multiprocessing
import pandas as pd
from scipy.spatial.distance import cosine

import kikundi.model
import kikundi.utils

logger = kikundi.utils.get_logger(__name__)


def extract_subgenre(label):
    
    # subgenres contain ---
    if '---' in label:
        # we consider rock-blues == rock blues == rock blue's
        label_s = label.split('---')[-1]
        label_r = label_s.replace(' ', '')\
                         .replace('-','')\
                         .replace("'",'')\
                         .replace('"','')\
                         .lower()
        
        # we consider rock/blues == blues/rock == bluesrock
        if '/' in label_r:
            split = label_r.split('/')
            sort_split = sorted(split)
            glued = ''.join(sort_split)
            return glued
        else:
            return label_r          
    else:
        return None
    

def occurrence_matrix(df):
    
    # create set of genres for each track
    all_sets = [set([y for y in s[1] if y == y]) for s in df.iterrows()]
    
    # extract unique list of subgenres
    extracted = [[extract_subgenre(l) for l in s] for s in all_sets]
    extracted = [list(set([l for l in x if l])) for x in extracted]

    # Get all unique subgenres
    daddy_set = set()
    for s in extracted:
        daddy_set.update(s)

    occurrences = OrderedDict(
        (l, OrderedDict((l, 0) for l in daddy_set)) 
        for l in daddy_set
    )

    # Find the co-occurrences:
    for l in extracted:
        for i in range(len(l)):
            for item in l[:i] + l[i + 1:]:
                occurrences[l[i]][item] += 1

    return pd.DataFrame(occurrences)


def compute_distance(comb):
    (s1, s2) = comb
    return {
        'subgenre1': s1.name, 
        'subgenre2': s2.name, 
        'distance': cosine(s1.values, s2.values)}


def filter_subgenres(occurrence_df, threshold):
    """
    Filter occurrence dataframe from occurrence_matrix() to include only subgenres with <threshold> co-occurrences
    """
    logger.info("Removing subgenres that do not co-occur more than {} times:".format(threshold))
    cols = list(occurrence_df.columns)
    for n,r in occurrence_df.iterrows():
        if sum(r) < threshold:
            cols.remove(n)

    filt_occurrence_df = occurrence_df.loc[cols, cols]
    logger.info("{} subgenres removed".format(len(occurrence_df)-len(filt_occurrence_df)))
    return filt_occurrence_df


def compute_distances(occurrence_df):
    comb = list(combinations([x[1] for x in occurrence_df.iterrows()], 2))
    logger.info('Computing cosine distance between subgenres')
    pool = Pool()
    results = pool.map(compute_distance, comb)

    distance_df = pd.DataFrame(results)
    
    # Make sure we have a distance in both directions
    distance_df_copy = distance_df.copy()
    distance_df_copy.columns = ['distance', 'subgenre2', 'subgenre1']
    distance_df_copy = distance_df_copy[['distance', 'subgenre1', 'subgenre2']]
    daddy_distance = pd.concat([distance_df, distance_df_copy]).fillna(0)
    distance_df_full = daddy_distance\
                        .groupby(['subgenre1', 'subgenre2'])\
                        .sum()\
                        .sort_values(by='distance')\
                        .reset_index()
    
    # Get square matrix as expected by scipy
    distance = distance_df_full\
                .pivot(index='subgenre1', columns='subgenre2', values='distance')\
                .fillna(0)
    
    return distance