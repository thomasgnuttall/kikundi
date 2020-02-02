import kikundi.utils
import matplotlib.pyplot as plt
import scipy.spatial.distance as ssd
import scipy.cluster.hierarchy as hcluster

logger = kikundi.utils.get_logger(__name__)

def hierarchical_clustering(distance_df, plot=False):
    """
    Cluster for all k from distance matrix <distance_df>. Pass a path to <plot> to write dendrogram to path
    """
    genres = [x.decode('utf-8') for x in list(distance_df.columns)]
    data = distance_df.values

    distVec = ssd.squareform(data)
    linkage = hcluster.linkage(distVec, method='ward')
    
    if plot:
        fig = plt.figure(figsize=(150,24))
        dendro  = hcluster.dendrogram(
            linkage,
            leaf_rotation=90, 
            leaf_label_func=lambda y: genres[y],
            leaf_font_size=12
            )
        logger.info('Writing dendrogram to {}'.format(plot))
        plt.xlabel('Subgenre')
        plt.ylabel('Cosine Distance')
        plt.savefig(plot)
        
    return hcluster.cut_tree(linkage, n_clusters=range(len(linkage)))