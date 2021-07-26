"""Logic pertraining to preparing the run files and folders."""
import copy
import logging
import shutil
from pathlib import Path

import toml

from haddock import modules_folder
from haddock.error import ConfigurationError


logger = logging.getLogger(__name__)


def setup_run(workflow_path):
    """
    Setup HADDOCK3 run.

    This function performs several actions in a pipeline.

    #1 : validate the parameter TOML file
    #2 : convert strings to paths where it should
    #3 : remove folder from previous runs if run folder name overlaps
    #4 : create the needed folders/files to start the run

    Returns
    -------
    dict
        A
        The updated parameter file.
    """
    params = toml.load(workflow_path)

    validate_params(params)
    convert_params_to_path(params)
    remove_folder(params['input']['project_dir'])
    create_begin_files(params)

    return params


def validate_params(params):
    """
    Validate the parameter file.

    #1 : checks for 'order' key
    #2 : checks for correct modules
    """
    order_exists(params)
    validate_modules(params)


def order_exists(params):
    """Confirms order key exists in config."""
    try:
        if 'order' not in params['input']:
            _msg = (
                "Workflow does not specify the execution 'order'. "
                "Please refer to DOCUMENTATION-LINK for more information.")
            raise ConfigurationError(_msg)
    except KeyError:
        _msg = (
            "Config file should have an 'input' section"
            "Please refer to DOCUMENTATION-LINK for more information.")
        raise ConfigurationError(_msg)
    return


def validate_modules(params):
    """Validate modules."""

    methods = (
        (package, params['stage'][package].get('method', 'default.py'))
        for package in params['input']['order']
        )

    for package, module in methods:
        module_loc = modules_folder / package / module
        if not module_loc.exists():
            _msg = (
                f"Method {package}:{module} not found in HADDOCK3 library. "
                "Please refer to the list of available modules at: "
                "DOCUMENTATION-LINK"
                )
            raise ConfigurationError(_msg)


def convert_params_to_path(params):
    """Convert parameters to path."""
    input_params = params['input']
    project_dir = Path(input_params['project_dir'])
    input_params['project_dir'] = project_dir.resolve()

    for mol_id, file_name in input_params['molecules'].items():
        file_path = Path(file_name)
        input_params['molecules'][mol_id] = file_path

    return


def remove_folder(folder):
    """Removes a folder if it exists."""
    if folder.exists():
        logger.warning(f'{folder} exists and it will be REMOVED!')
        shutil.rmtree(folder)


def create_begin_files(params):
    """Create initial files for HADDOCK3 run."""
    project_dir = params['input']['project_dir']
    data_dir = project_dir / 'data'
    begin_dir = project_dir / 'begin'

    project_dir.mkdir()
    begin_dir.mkdir()
    data_dir.mkdir()

    for mol_id, mol_path in params['input']['molecules'].items():
        shutil.copy(mol_path, data_dir)

        begin_mol = (begin_dir / f'{mol_id}.pdb').resolve()
        shutil.copy(mol_path, begin_mol)

        params['input']['molecules'][mol_id] = begin_mol