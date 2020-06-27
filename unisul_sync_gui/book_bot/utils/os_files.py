import os
import json


def file_exists(directory, filename):
    return os.path.exists(os.path.join(directory, filename))


def maybe_create_dir(directory):
    if not (os.path.exists(directory) or os.path.isdir(directory)):
        os.makedirs(directory)


def open_sync_file(directory, filename, mode, make_dir=True):
    if make_dir:
        maybe_create_dir(directory)
    return open(os.path.join(directory, filename), mode) 


def load_sync_data(directory, filename, default=[]):
    if not file_exists(directory, filename):
        return default
    with open_sync_file(directory, filename, 'rb') as file:
        return json.load(file)