from unisul_sync_gui import dist_util

import os
import subprocess
from pathlib import Path


def test_list_every_file_in_directory(tmp_path):
    # create 5 dummy files inside a directory
    for i in range(5):
        root_dir = tmp_path / Path(f'foo-{i}')
        root_dir.mkdir()

        # touch file on disk
        with open(root_dir / Path(str(i)), 'w') as _: pass

    result = dist_util.list_files(tmp_path)

    assert len(list(result)) == 5


def test_find_icons_dirname_when_bundled(with_bundled):
    expected_dir = '/foo'

    with_bundled(expected_dir)

    result = dist_util.find_icons_dirname()
    assert result == expected_dir


def test_pip_weak_requirements_fails_with_false(monkeypatch):
    expected_err = 'bar'

    def _run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, 
                                            None, 
                                            stderr=bytes(expected_err, 'utf-8'))

    def _assert_err(error):
        assert expected_err == error

    monkeypatch.setattr(subprocess, 'run', _run)

    result = dist_util.pip_weak_requirements(on_error=_assert_err)
    assert result is False
