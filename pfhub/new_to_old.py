"""Module to convert a pfhub.yaml to meta.json (new to old)
"""

import re
import os
import textwrap

from dotwiz import DotWiz
from toolz.curried import get, pipe, assoc_in, curry, assoc, get_in
from toolz.curried import map as map_
from toolz.curried import filter as filter_

from .func import read_yaml, render, write_files, isabs, makeabs


def to_old(path, dest):
    """Convert from new schema to old schema

    Args:
      path: the path to the YAML file
      dest: destination directory for output files

    Returns:
      the paths for the output files
    """
    return pipe(
        path,
        read_yaml,
        DotWiz,
        fix_data_urls(os.path.dirname(makeabs(path))),
        DotWiz,
        render_meta,
        lambda x: write_files({"meta.yaml": x}, dest),
    )


@curry
def fix_data_urls(base_path, data_all):
    """Add the abosulte paths to the data items in meta.yaml

    Args:
      base_path: the base path of the meta.yaml
      data_all: all the data from the pfhub.yaml

    Returns:
      all the data from the pfhub.yaml with updated data item paths
    """
    add_base_path = lambda x: x if isabs(x) else os.path.join(base_path, x)
    update = lambda x: assoc(x, "url", add_base_path(x.name))

    return pipe(
        data_all.results.dataset_temporal,
        map_(update),
        list,
        assoc_in(data_all, ["results", "dataset_temporal"]),
    )


def get_github_id(str_):
    """Get a GitHub ID from a string

    Args:
      str_: a string

    Returns:
      the GitHub ID or None

    >>> print(get_github_id("github: wd15"))
    wd15

    >>> print(get_github_id("wd15"))
    <BLANKLINE>

    """

    github_ = re.match(r"github:(.*)", str_)
    if github_:
        return github_.groups()[0].strip()
    return ""


def subs(data_all, lines_and_contours):
    """Dict substitution for new to old schema transform

    Args:
      data_all: all the input data as dotwiz object
      lines_and_contours: dictionary of lines and contours

    Returns:
      a substitution dict
    """
    github_id = get_github_id(data_all.contributors[0].id)

    return {
        "first": get(0, data_all.contributors[0].name.split(" "), ""),
        "last": get(1, data_all.contributors[0].name.split(" "), ""),
        "github_id": github_id if github_id else "",
        "summary": textwrap.indent(data_all.summary, "    "),
        "timestamp": data_all.date_created,
        "cpu_architecture": data_all.results.hardware.architecture,
        "acc_architecture": "none",
        "parallel_model": "",
        "clock_rate": "0.0",
        "cores": data_all.results.hardware.cores,
        "nodes": data_all.results.hardware.nodes,
        "benchmark_id": data_all.benchmark_problem.split(".")[0],
        "benchmark_version": data_all.benchmark_problem.split(".")[1],
        "software_name": data_all.framework[0].name,
        "container_url": "",
        "repo_url": data_all.framework[0].url,
        "wall_time": data_all.results.time_in_s,
        "sim_time": data_all.results.fictive_time,
        "memory_usage": data_all.results.memory_in_kb,
        "lines": lines_and_contours["lines"],
        "contours": lines_and_contours.get("contours", []),
        "name": data_all.id,
        "repo_version": "aaaaa",
    }


def render_meta(data_all):
    """Render the meta file"""
    return render(
        "pfhub_meta", subs(data_all, {"lines": get_lines(data_all), "contours": []})
    )


def get_lines(data_all):
    """Build the lines list of substitutions"""

    def get_line(item):
        return {
            "description": "",
            "url": item.url,
            "ext_type": item.name.split(".")[1],
            "name": data_name_to_old(item.name, data_all),
            "x_field": item.columns[0],
            "y_field": item.columns[1],
        }

    return pipe(data_all.results.dataset_temporal, map_(get_line), list)


def data_name_to_old(pfhub_name, data_all):
    """Translate data name from pfhub.yaml into meta.yaml

    Args:
      pfhub_name: the pfhub.yaml data name
      data_all: all the data from the pfhub.yaml file

    Returns:
      corresponding name in meta.yaml schema
    """
    get_data_file = lambda x: os.path.join(
        os.path.dirname(__file__), "templates", f"{x}_data.yaml"
    )
    return pipe(
        data_all.benchmark_problem.split(".")[0],
        get_data_file,
        read_yaml,
        filter_(lambda x: x["schema"]["name"] == pfhub_name),
        list,
        get_in([0, "name"]),
    )
