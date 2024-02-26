from zenodo_client import Creator, Metadata, ensure_zenodo
from pprint import pprint
import uuid
from dotwiz import DotWiz
from toolz.curried import map as map_
from toolz.curried import get, pipe, pluck, get_in

from .func import read_yaml

from pprint import pprint

import pathlib


def upload_to_zenodo(path, sandbox):
    return ensure_zenodo_(
        pathlib.Path(path).resolve(),
        sandbox=sandbox
    ).json()['links']['html']


def ensure_zenodo_(resolved_path, sandbox=True):
    return ensure_zenodo(
        key=str(uuid.uuid4()),
        data=Metadata(
            title='PFHub Upload',
            upload_type='dataset',
            description= get_summary(resolved_path),
            creators = get_creators(resolved_path)
        ),
        paths=[str(resolved_path)] + get_data_paths(resolved_path),
        sandbox=sandbox,
    )


def get_data_paths(resolved_path):
    return pipe(
        resolved_path,
        read_yaml,
        get('results'),
        get('dataset_temporal'),
        pluck('name'),
        map_(resolved_path.parent.joinpath),
        map_(str),
        list
    )


def get_creators(resolved_path):
    return pipe(
        resolved_path,
        read_yaml,
        DotWiz,
        get('contributors'),
        map_(get_creator),
        list
    )


def get_creator(contributor):
    print(contributor.affiliation)
    return Creator(
        name=contributor.name,
        affiliation=get_in(['affiliation', 0], None),
    )


def get_summary(resolved_path):
    return pipe(
        resolved_path,
        read_yaml,
        get('summary'),
    )
