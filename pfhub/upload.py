"""Tools for uploading PFHub results to Zenodo
"""

import uuid
import pathlib

from zenodo_client import Creator, Metadata, ensure_zenodo
from dotwiz import DotWiz
from toolz.curried import map as map_
from toolz.curried import get, pipe, pluck, get_in

from .func import read_yaml


def upload_to_zenodo(path, sandbox):
    """Main function for uploading to Zenodo

    Args:
      path: direct path to the pfhub.yaml file
      sandbox: whether to upload to sandbox.zenodo.org

    Returns:
      the URL to the new record
    """
    return ensure_zenodo_(pathlib.Path(path).resolve(), sandbox=sandbox).json()[
        "links"
    ]["html"]


def ensure_zenodo_(resolved_path, sandbox=True):
    """Call the zenodo_client's ensure_zenodo function

    Args:
      resolved_path: the resolved path to pfhub.yaml
      sandbox: whether to upload to sandbox.zenodo.org

    Returns:
      the reply from zenodo.org
    """
    return ensure_zenodo(
        key=str(uuid.uuid4()),
        data=Metadata(
            title="PFHub Upload",
            upload_type="dataset",
            description=get_summary(resolved_path),
            creators=get_creators(resolved_path),
        ),
        paths=[str(resolved_path)] + get_data_paths(resolved_path),
        sandbox=sandbox,
    )


def get_data_paths(resolved_path):
    """Get the paths to the data files from the pfhub.yaml

    Args:
      resolved_path: the resolved path to the pfhub.yaml

    Returns:
      list of paths to data files
    """
    return pipe(
        resolved_path,
        read_yaml,
        get("results"),
        get("dataset_temporal"),
        pluck("name"),
        map_(resolved_path.parent.joinpath),
        map_(str),
        list,
    )


def get_creators(resolved_path):
    """Extract the creators

    Args:
      resolved_path: the resolved path to the pfhub.yaml

    Returns:
      list of contributors
    """
    return pipe(
        resolved_path, read_yaml, DotWiz, get("contributors"), map_(get_creator), list
    )


def get_creator(contributor):
    """Get creator from a contributor

    Args:
      contributor: pfhub's contributor

    Returns:
      zenodo style creator
    """
    return Creator(
        name=contributor.name,
        affiliation=get_in(["affiliation", 0], None),
    )


def get_summary(resolved_path):
    """Extract the summary from the yaml file

    Args:
      resolved_path: the resolved path to the pfhub.yaml

    Returns:
      the summary text
    """
    return pipe(
        resolved_path,
        read_yaml,
        get("summary"),
    )
