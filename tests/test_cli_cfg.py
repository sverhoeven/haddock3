"""Test haddock3-cfg client."""
import pytest

from haddock import config_expert_levels
from haddock.clis import cli_cfg
from haddock.modules import modules_category


@pytest.fixture(params=config_expert_levels + ("all",))
def config_level(request):
    """Haddock3 config levels."""
    return request.param


@pytest.mark.parametrize(
    "module",
    list(modules_category.keys()),
    )
def test_export_cfgs(module, config_level):
    """Test export all configs work."""
    cli_cfg.main(module, config_level)
