#!/usr/bin/env python

import argparse
import os
import platform
import sys

__version__ = '0.3'

PY2_PACKAGES = [
    'weave',
    'functools32',
    'futures',
    'subprocess32',
    'backports.weakref',
    'backports.functools_lru_cache',
    'backports_abc',
    'pathlib2',
    'funcsigs',
    'pathlib2',
]


def filter_line(line):
    line = line.strip()
    if line.startswith('#'):
        line = ''
    return line


def read_env(path):
    with open(path, 'r') as f:
        return list(filter(None, map(filter_line, f)))


def cook_yaml(
    python_version='3',
    channel='defaults',
    name='ab',
    prefix=None,
    conda_paths=['conda.txt'],
    pip_paths=[],
    mpi=None,
    pypy=False,
):
    conda_envs = sum((read_env(conda_path) for conda_path in conda_paths), [])
    pip_envs = sum((read_env(pip_path) for pip_path in pip_paths), [])

    dict_ = dict()

    # channel
    dict_['channels'] = {
        'conda-forge': ['conda-forge'],
        'defaults': ['defaults', 'conda-forge'],
        'intel': ['intel', 'defaults', 'conda-forge'],
    }[channel]

    dict_['dependencies'] = conda_envs
    if platform.system() == 'Darwin':
        dict_['dependencies'] += ['python.app']

    # python_version
    python_version_major = python_version[0]
    if pypy:
        dict_['dependencies'] += ['pypy', f'pypy{python_version}']
    else:
        dict_['dependencies'].append(f'python={python_version}')
    if channel == 'intel':
        dict_['dependencies'].append(f'intelpython{python_version_major}_core')
    if python_version_major == 2:
        dict_['dependencies'] += PY2_PACKAGES
        # conda cannot resolve subprocess32 and mypy in python2
        try:
            dict_['dependencies'].remove('mypy')
        except ValueError:
            pass

    if mpi == 'cray':
        print('Install mpi4py compiled using Cray compiler from cray-mpi4py.sh', file=sys.stderr)
    elif mpi in ('mpich', 'openmpi'):
        dict_['dependencies'].append(f'mpi4py::{mpi}')
        dict_['dependencies'].append('mpi4py::mpi4py')
    else:
        dict_['dependencies'].append('mpi4py')

    dict_['dependencies'].append({
        'pip': pip_envs
    })

    # name
    dict_['name'] = f'{name}{"".join(python_version.split("."))}-{channel}' + ('' if mpi is None else f'-{mpi}')
    # prefix
    if prefix:
        dict_['prefix'] = os.path.join(prefix, dict_['name'])
    return dict_


def cli():
    parser = argparse.ArgumentParser(description='Generate conda environment YAML file.')

    parser.add_argument('-o', '--yaml', type=argparse.FileType('w'), default=sys.stdout,
                        help="Output YAML.")
    parser.add_argument('-v', '--version', type=str, default='3',
                        help='python version. 2, 3, or 3.x. Default: 3')
    parser.add_argument('--pypy', action='store_true',
                        help='install pypy, install CPython if not specified')
    parser.add_argument('-c', '--channel', default='defaults',
                        help='conda channel. e.g. intel, defaults. Default: defaults')
    parser.add_argument('-n', '--name', default='ab',
                        help='prefix of the name of environment. Default: ab')
    parser.add_argument('-p', '--prefix',
                        help="Full path to conda environment prefix. If not specified, conda's default will be used.")
    parser.add_argument('-C', '--conda-txt', nargs='+',
                        help="path to a file that contains the list of conda packages to be installed. Can be more than 1.")
    parser.add_argument('-P', '--pip-txt', nargs='+',
                        help="path to a file that contains the list of pip packages to be installed. Can be more than 1.")
    parser.add_argument('-m', '--mpi',
                        help="custom version of mpi4py if sepecified. e.g. mpich/openmpi to use mpich/openmpi from the mpi4py channel; cray to custom build using cray compiler.")

    parser.add_argument('-V', action='version',
                        version='%(prog)s {}'.format(__version__))

    args = parser.parse_args()

    dict_ = cook_yaml(
        python_version=args.version,
        channel=args.channel,
        name=args.name,
        prefix=args.prefix,
        conda_paths=args.conda_txt,
        pip_paths=args.pip_txt,
        mpi=args.mpi,
        pypy=args.pypy,
    )
    try:
        import yaml
        yaml.dump(dict_, args.yaml, default_flow_style=False)
    except ImportError:
        import json
        print(json.dumps(dict_), file=args.yaml)


if __name__ == "__main__":
    cli()
