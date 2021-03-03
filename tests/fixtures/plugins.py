from unisul_sync_gui import plugins
import pytest

import secrets
from pathlib import Path


@pytest.fixture
def plugin_manager(tmp_path):
    def factory(plugin_code):
        # use a random module name so python can't remember it
        module_name = f'{secrets.token_hex(4)}.py'
        
        plugin_path = tmp_path / Path(module_name)
        with open(plugin_path, 'w') as fd:
            fd.write(plugin_code)

        lookup_paths = [str(tmp_path)]
        return plugins.PluginManager(lookup_paths)

    return factory