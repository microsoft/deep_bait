import logging
import os

import fire
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from toolz import pipe, curry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _read_notebook(filename):
    return nbformat.read(filename, as_version=4)


@curry
def _write_notebook(notebook_filename, nb):
    logger.info('Writing notebook to {}'.format(notebook_filename))
    nbformat.write(nb, notebook_filename)


def _parameter_cell_from(nb):
    for cell in nb.cells:
        if cell['cell_type'] == 'code' and cell['source'].startswith('# Parameters'):
            return cell


def _extract_text(cell):
    return cell['outputs'][0]['text']


def _parameters_dict_from(cell):
    valid_lines_gen = (line for line in cell['source'].split('\n') if not line.startswith('#') and '=' in line)
    return dict(
        ((line.split('=')[0].strip(), {'orig': line, 'value': line.split('=')[1].strip()}) for line in valid_lines_gen))


def _compose(param, param_value):
    return '{}={}'.format(param, param_value)

@curry
def _execute_nb(nb, kernel='python3'):
    logger.info('Executing notebook with kernel {}'.format(kernel))
    ep = ExecutePreprocessor(timeout=None, kernel_name=kernel)
    _ = ep.preprocess(nb, {'metadata': {'path': os.getcwd()}})
    return nb


def _replace_in_parameter_string(orig_string, parameters_dict):
    for key, val_dict in parameters_dict.items():
        orig_string = orig_string.replace(val_dict['orig'], _compose(key, val_dict['value']))
    return orig_string


def _parameterise_notebook(nb, **kwargs):
    p_cell = _parameter_cell_from(nb)
    parameters_dict = _parameters_dict_from(p_cell)
    for key, value in kwargs.items():
        logger.info('Setting {} to {}'.format(key, value))
        if key not in parameters_dict:
            raise ValueError('Parameter {} does not exist in Notebook'.format(key))

        if isinstance(value, str):
            parameters_dict[key]['value'] = "'{}'".format(value)
        else:
            parameters_dict[key]['value'] = "{}".format(value)

    p_cell['source'] = _replace_in_parameter_string(p_cell['source'], parameters_dict)
    return nb


def _main(filename, to_filename, kernel='python3', **kwargs):
    logger.info('Processing {}'.format(filename))
    pipe(filename,
         _read_notebook,
         lambda nb: _parameterise_notebook(nb, **kwargs),
         _execute_nb(kernel=kernel),
         _write_notebook(to_filename))


if __name__ == '__main__':
    fire.Fire(_main)
