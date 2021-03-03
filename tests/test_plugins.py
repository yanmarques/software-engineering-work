from unisul_sync_gui import plugins

import sys


def test_plugin_manager_keep_original_sys_path(plugin_manager):
    expected_sys_path = sys.path.copy()

    plugin_code = '''
def plugin():
    raise Exception('Something bad')
'''
    manager = plugin_manager(plugin_code)

    try:
        manager.register_from_paths()
    except:
        pass

    assert sys.path == expected_sys_path


def test_plugin_manager(plugin_manager):
    expected = 'foo'

    plugin_code = '''
def plugin():
    return 'foo'
'''
    manager = plugin_manager(plugin_code)
    manager.register_from_paths()

    assert manager._objs[0] == expected