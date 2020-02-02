import numpy as np
from scipy.spatial.distance import euclidean
import kikundi.utils

logger = kikundi.utils.get_logger(__name__)

def DaviesBouldin(X, labels):
    n_cluster = len(np.bincount(labels))
    cluster_k = [X[labels == k] for k in range(n_cluster)]
    centroids = [np.mean(k, axis = 0) for k in cluster_k]
    variances = [np.mean([euclidean(p, centroids[i]) for p in k]) for i, k in enumerate(cluster_k)]
    db = []

    for i in range(n_cluster):
        for j in range(n_cluster):
            if j != i:
                db.append((variances[i] + variances[j]) / euclidean(centroids[i], centroids[j]))

    return(np.max(db) / n_cluster)


def evaluate(occurence_df, clustering_results):
	logger.info('Evaluating the clustering of {} subgenres into clusters of size 2-100'.format(len(clustering_results)))
	X = occurence_df.values
	return [DaviesBouldin(X, clustering_results[:,i]) \
			for i in range(len(clustering_results))[2:100]]