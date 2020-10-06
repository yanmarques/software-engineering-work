import unisul_sync_gui

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers()
    cfg_parser = subparsers.add_parser('config')
    cfg_parser.add_argument('--get', 
                            metavar='KEY', 
                            help='Retrieve a configuration parameter.')

    return parser.parse_args()


def entrypoint():
    args = parse_args()
    if 'get' in args:
        # get configuration
        config = unisul_sync_gui.config.load()
        if args.get in config:
            print(config[args.get])
    else:
        # start app
        unisul_sync_gui.main()