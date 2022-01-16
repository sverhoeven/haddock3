"""
Extract the default configuration file for each module.

By default presents the parameters from the three expertise levels:
    `basic`, `intermediate`, and `guru`.

USAGE:
    $ haddock3-cfg -m MODULE
    $ haddock3-cfg -m MODULE -l LEVEL
"""
import argparse
import importlib
import sys
from pathlib import Path

from haddock.gear.yaml2cfg import yaml2cfg_text_with_explevels
from haddock.libs.libio import read_from_yaml
from haddock.modules import modules_category


ap = argparse.ArgumentParser(
    prog="HADDOCK3 config retriever",
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )

ap.add_argument(
    "-m",
    dest="module",
    help="The module for which you want to retrieve the default configuration.",
    required=True,
    choices=sorted(modules_category.keys()),
    )

ap.add_argument(
    "-l",
    dest="explevel",
    required=False,
    help="The expertise level of the parameters. Defaults to \"all\".",
    default="all",
    choices=("basic", "intermediate", "guru", "all"),
    )


# command-line client helper functions
# load_args, cli, maincli
def load_args(ap):
    """Load argument parser args."""
    return ap.parse_args()


def cli(ap, main):
    """Command-line interface entry point."""
    cmd = load_args(ap)
    main(**vars(cmd))


def maincli():
    """Execute main client."""
    cli(ap, main)


def main(module, explevel):
    """Extract the default configuration file for a given module."""
    module_name = ".".join((
        'haddock',
        'modules',
        modules_category[module],
        module,
        ))
    module_lib = importlib.import_module(module_name)
    cfg = module_lib.DEFAULT_CONFIG

    ycfg = read_from_yaml(cfg)

    if explevel == "all":
        new_config = yaml2cfg_text_with_explevels(ycfg, module)

    else:
        new_config = yaml2cfg_text_with_explevels(
            ycfg,
            module,
            expert_levels=[explevel],
            )

    Path(f"haddock3_{module}.cfg").write_text(new_config)

    return 0


if __name__ == "__main__":
    sys.exit(maincli())
