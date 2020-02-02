import kikundi.evaluation
import kikundi.utils
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

logger = kikundi.utils.get_logger(__name__)


def report(run_id, clustering, occurence_df, setup):
	"""
	Store all run information, plots, results and configuration
	"""
	X = occurence_df.values

	logger.info('Computing Davies Bouldin Index for k=2:100')
	y = [kikundi.evaluation.DaviesBouldin(X, clustering[:,i]) \
					for i in range(len(clustering))[2:100]]
	X = range(2,100)

	plot_db(X, y, run_id, 'results/plots/{}_DaviesBouldin.png'.format(run_id))
	report_run(run_id, setup, (X, y))


def plot_db(X, y, title=None, save_path=None):
	"""
	plot results from David Bouldin Analysis and save at <save_path>
	"""
	plt.figure(figsize=(10,10))
	plt.plot(X, y)
	plt.ylabel('Davies Bouldin Index', fontsize=15)
	plt.xlabel('Number of Clusters', fontsize=15)
	if title:
		plt.title(title, fontsize=18)
	if save_path:
		logger.info('Writing plot to {}'.format(save_path))
		plt.savefig(save_path)


def report_run(run_id, setup, clustering_result, path='results/results.csv'):
	"""
	Append run conf and results to results.csv at <path>
	"""
	logger.info('Generating report for run {}'.format(run_id))
	X, y = clustering_result
	row = {
		'data':'; '.join(['{}_:_{}'.format(k,v) for k,v in setup['dataframes'].items()]),
		'index': setup['index'],
		'threshold':setup['threshold'],
		'git_describe':kikundi.utils.git_describe(),
		'run_id':run_id
	}
	results_dict = {'DavidBouldin_at_k={}'.format(i):db for i,db in zip(X,y)}
	row.update(results_dict)

	df = pd.DataFrame({k: [v] for k,v in row.items()})

	old_df = pd.read_csv(path)

	for col in old_df:
	    if col not in df:
	        df[col] = np.nan
	for col in df:
	    if col not in old_df:
	        old_df[col] = np.nan

	new_df = pd.concat([old_df, df], sort=True)
	logger.info('Writing to {}'.format(path))
	new_df.to_csv(path, header=True, index=False)

