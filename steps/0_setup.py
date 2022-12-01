import time
import yaml
import os
from shutil import copyfile

def setup(args):
    config_path = args.conf_dir
    config = yaml.load(open(config_path, 'r'), Loader=yaml.FullLoader)
    work_path = config['Data']['work_path']

    if not os.path.exists(work_path):
        os.makedirs(work_path)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_dir', default = 'configuration.yaml')

    args = parser.parse_args()
    setup(args)
