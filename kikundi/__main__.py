#############################################
#############################################
###    _  ___ _                    _ _    ###
###   | |/ (_) | ___   _ _ __   __| (_)   ###
###   | ' /| | |/ / | | | '_ \ / _` | |   ###
###   | . \| |   <| |_| | | | | (_| | |   ###
###   |_|\_\_|_|\_\\__,_|_| |_|\__,_|_|   ###
###                                       ### 
#############################################
###=======================================###
###   v1.0 | 2019/01/29 | Thomas Nuttall  ###
###=======================================###
#############################################
 
import sys

import click

import kikundi.evaluation
import kikundi.feature_extraction
import kikundi.model
import kikundi.persistence
import kikundi.reporting
import kikundi.utils

logger = kikundi.utils.get_logger(__name__)


@click.group()
def cli():
    pass


@cli.command(name="run-pipeline")
@click.argument('config-filenames', nargs=-1)
@click.option('--report/--do-not-report', default=False, help='Report evalution and plots')
def cmd_run_pipeline(config_filenames, report=False):
    run_pipeline(config_filenames=config_filenames, report=report)


def run_pipeline(config_filenames, report):
    """
    Run full task pipeline
    """
    kikundi.utils.package_banner() 

    run_id = kikundi.utils.generate_unique_id()
    logger.info('Commencing run with id {}'.format(run_id))
    conf_contents = kikundi.utils.load_configuration(config_filenames)
    setup = conf_contents['setup']

    ###################
    #### DATA LOAD ####
    ###################
    index = setup['index']

    all_frames = {}
    for i,(k,v) in enumerate(setup['dataframes'].items()):
        logger.info('Loading dataframe {} from {}'.format(k, v))
        df = kikundi.utils.load_dataframe(v)
        all_frames[k] = kikundi.utils.decorate_columns(df, '_'+k, index)
    
    joined = kikundi.utils.join_dataframes(
            all_frames.values(), 
            index=index
        )


    #############################
    #### FEATURE/ EXTRACTION ####
    #############################
    threshold = setup['threshold']

    cols = [x for x in joined.columns if 'recordingm' not in x and 'releasegroupm' not in x]
    selected = joined[cols]

    occurrence_df = kikundi.feature_extraction.occurrence_matrix(selected)
    filt_occurrence_df = kikundi.feature_extraction.filter_subgenres(occurrence_df, threshold=threshold)
    distance_df = kikundi.feature_extraction.compute_distances(filt_occurrence_df)

    
    ###################
    #### MODELLING ####
    ###################

    clustering = kikundi.model.hierarchical_clustering(distance_df, plot='results/plots/{}_dendrogram.png'.format(run_id))


    ###################
    #### EVALUATION ###
    ###################

    results = kikundi.evaluation.evaluate(filt_occurrence_df, clustering)


    ##################
    #### REPORTING ###
    ##################
    if report:
        kikundi.reporting.report(run_id, clustering, filt_occurrence_df, setup)


if __name__ == '__main__':
    cli()
