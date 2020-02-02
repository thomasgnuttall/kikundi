import datetime
import hashlib
import logging
import pandas as pd
import subprocess
import uuid

def get_logger(name):
    logging.basicConfig(format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


logger = get_logger(__name__)


class ConfigError(Exception):
    pass


def package_banner():
	banner = """


         _  ___ _                    _ _ 
        | |/ (_) | ___   _ _ __   __| (_)
        | ' /| | |/ / | | | '_ \ / _` | |
        | . \| |   <| |_| | | | | (_| | |
        |_|\_\_|_|\_\\___,_|_| |_|\__,_|_|
                                         

        

	""".split("\n")
	for l in banner:
		logger.info(l)


def sha1(s):
	"""Hash input string, <s> to SHA-1"""
	return hashlib.sha1(str(s)).hexdigest()


def load_dataframe(path, sep='\t'):
    """
    Load dataframe at <path> with seperator <sep>
    Returns: pd.DataFrame
    """
    df = pd.read_csv(path, sep=sep, low_memory=False)
    col, row = df.shape
    logger.info('{} rows and {} columns'.format(col, row))
    return df


def join_dataframes(dfs, index, how='inner'):
    """
    Join list of dataframes on <index>
    """
    logger.info('Joining {} dataframes on {}'.format(len(dfs), index))
    df = dfs[0]
    for d in dfs[1:]:
        df = df.merge(d, on=index, how=how)
    logger.info('Final frame length: {}'.format(len(df)))
    return df


def decorate_columns(df, suffix, exceptions):
    """
    Add <suffix> to dataframe columns not in <exceptions>
    """
    df2 = df.copy(deep=True)
    df2.columns = [x+suffix if x not in exceptions else x for x in df2.columns]
    return df2


def load_configuration(config_filenames):
    """
    Load and merge config dicts from list of strings
    """
    import kikundi.persistence
    if not config_filenames:
        raise ConfigError("No config files!")

    # Load configuration
    conf_contents = {}
    for fname in config_filenames:
        logger.info('Loading config file {}'.format(fname))
        f = kikundi.persistence.load_yaml(fname)
        # TODO: ensure duplicate keys are handled correctly
        conf_contents.update(f)

    return conf_contents


def generate_unique_id():
    return str(uuid.uuid4())


def git_describe():
    return subprocess.Popen(
        ['git', 'describe', '--dirty', '--always', '--long'], 
        stdout=subprocess.PIPE
    ).communicate()[0].decode('utf-8').replace('\n', '')
    

