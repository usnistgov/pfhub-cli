"""The CLI command line tool
"""

import re
import os
import tempfile
import shutil
import sys
import pathlib

import click
import click_params
from toolz.curried import pipe, get, curry, assoc, unique, concat
from toolz.curried import map as map_
import pykwalify
import pykwalify.core
import requests
import linkml.validators.jsonschemavalidator as validator
import papermill as pm

from .. import test as pfhub_test
from ..convert import meta_to_zenodo_no_zip, download_file, get_name
from ..convert import download_zenodo as download_zenodo_
from ..convert import download_meta as download_meta_
from ..func import compact, read_yaml, make_id, add_list_items, makeabs
from ..func import clear_cache as clear_cache_
from ..new_to_old import to_old
from ..upload import upload_to_zenodo


f_result_list = (
    lambda: pathlib.Path(__file__).parent.resolve() / ".." / "simulation_list.yaml"
)


EPILOG = "See the documentation at https://pages.nist.gov/pfhub-cli"


@click.group(epilog=EPILOG)
def cli():
    """Submit results to PFHub and manipulate PFHub data"""


@cli.command(epilog=EPILOG)
@click.argument("url", type=click_params.URL)
@click.option(
    "--dest",
    "-d",
    help="destination directory",
    default="./",
    type=click.Path(exists=True, writable=True, file_okay=False),
)
def download_zenodo(url, dest):
    """Download a Zenodo record

    Works with any Zenodo link

    Args:
      url: the URL of a Zenodo record
      dest: the destination directory
    """
    record_id = get_zenodo_record_id(url, zenodo_regexs())
    sandbox = False
    if record_id is None:
        record_id = get_zenodo_record_id(url, zenodo_sandbox_regexs())
        sandbox = True

    if record_id is not None:
        local_filepaths = download_zenodo_(record_id, sandbox=sandbox, dest=dest)
        output(local_filepaths)
    else:
        click.secho(f"{url} does not match any expected regex for Zenodo", fg="red")
        sys.exit(1)


@cli.command(epilog=EPILOG)
@click.argument(
    "record",
    type=click_params.FirstOf(click_params.URL, click.STRING, return_param=True),
)
@click.option(
    "--dest",
    "-d",
    help="destination directory",
    default="./",
    type=click.Path(exists=True, file_okay=False, writable=True),
)
def download(record, dest):
    """Download a PFHub record

    In addition, gets the linked data in the `data` section

    Args:
      record: the name of the result on PFHub (or URL to a meta.yaml)
      dest: the destination directory
    """
    param, value = record

    if repr(param) == "STRING":
        regex = re.fullmatch(r".*10.5281/zenodo.(\d{1,})", value)
        if regex is None:
            base = "https://raw.githubusercontent.com/usnistgov/pfhub/"
            end = f"master/_data/simulations/{value}/meta.yaml"
            url = os.path.join(base, end)
        else:
            record_id = regex.groups()[0]
            zenodo_url = f"https://doi.org/10.5281/zenodo.{record_id}"
            download_zenodo.callback(zenodo_url, dest)
            sys.exit(0)
    else:
        url = value

    try:
        is_meta = validate_old_url(url)
    except requests.exceptions.ConnectionError as err:
        click.secho(err, fg="red")
        click.secho(f"{url} is invalid", fg="red")
        sys.exit(1)
    except IsADirectoryError:
        click.secho(f"{url} is not a link to a file", fg="red")
        sys.exit(1)

    if is_meta:
        local_filepaths = download_meta_(url, dest=dest)
        output(local_filepaths)
    else:
        click.secho(f"{url} is not valid", fg="red")
        sys.exit(1)


@cli.command(epilog=EPILOG)
@click.argument(
    "file_path", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    "--dest",
    "-d",
    help="destination directory",
    default="./",
    type=click.Path(exists=False, writable=True, file_okay=False),
)
def convert(file_path, dest):
    """Convert between formats (old PFHub schema to new PFHub schema)

    Args:
      file_path: the file path to the old style PFHub YAML
      dest: the destination directory

    """
    is_meta = validate_old_(file_path)
    if is_meta:
        local_filepaths = meta_to_zenodo_no_zip(file_path, dest)
        output(local_filepaths)
    else:
        click.secho(f"{file_path} is not valid", fg="red")
        sys.exit(1)


@cli.command(epilog=EPILOG)
@click.argument(
    "file_path", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    "--dest",
    "-d",
    help="destination directory",
    default="./",
    type=click.Path(exists=False, writable=True, file_okay=False),
)
def convert_to_old(file_path, dest):
    """Convert between formats (new PFHub schema to old PFHub schema)

    Args:
      file_path: path to PFHub YAML file
      dest: the destination directory

    """
    is_valid = validate_(file_path)
    if is_valid:
        local_filepaths = to_old(file_path, dest)
        output(local_filepaths)
    else:
        click.secho(f"{file_path} is not valid", fg="red")
        sys.exit(1)


@cli.command(epilog=EPILOG)
@click.argument(
    "file_path", type=click.Path(exists=True, dir_okay=False, readable=True)
)
def validate_old(file_path):
    """Validate a YAML file with the old PFHub schema

    Args:
      file_path: the URL of the meta.yaml

    """
    if validate_old_(file_path):
        click.secho(f"{file_path} is valid", fg="green")
    else:
        click.secho(f"{file_path} is not valid", fg="red")
        sys.exit(1)


@cli.command(epilog=EPILOG)
@click.argument(
    "file_path", type=click.Path(exists=True, dir_okay=False, readable=True)
)
def validate(file_path):
    """Validate a YAML file with the new PFHub schema

    Args:
      file_path: the URL of the meta.yaml

    """
    if validate_(file_path):
        click.secho(f"{file_path} is valid", fg="green")
    else:
        click.secho(f"{file_path} is not valid", fg="red")
        sys.exit(1)


@cli.command(epilog=EPILOG)
def generate_yaml(file_path):  # pylint: disable=unused-argument
    """(Not implemented) Infer a PFHub YAML file from GitHub ID, ORCID,
    benchmark ID and/or existing record.
    """


@cli.command(epilog=EPILOG)
@click.option("--benchmark-id", "-b", type=click.Choice(["1a.1"]), multiple=True)
@click.option("--clear-cache/--no-clear-cache", default=False)
@click.option(
    "--dest",
    "-d",
    help="destination directory",
    default="./",
    type=click.Path(exists=True, writable=True, file_okay=False),
)
@click.option(
    "--result-yaml",
    "-r",
    help="Local meta.yaml or pfhub.yaml file to add to results",
    multiple=True,
    type=click_params.FirstOf(
        click_params.URL,
        click.Path(exists=True, writable=False, dir_okay=False),
        name="url path",
        return_param=False,
    ),
)
@click.option(
    "--result-list",
    "-l",
    help="URL or path to YAML file with list of simulation results",
    default=str(f_result_list()),
    type=click_params.FirstOf(
        click_params.URL,
        click.Path(exists=True, writable=False, dir_okay=False),
        name="url path",
        return_param=True,
    ),
)
def render_notebook(benchmark_id, clear_cache, dest, result_yaml, result_list):
    """Render the comparison notebook for the corresponding benchmark ID."""
    if clear_cache:
        clear_cache_()

    def raise_error(benchmark_ids):
        if len(benchmark_ids) == 0:
            click.secho(
                "Requires either --benchmark_id or --result-yaml to be specified",
                fg="red",
            )
            sys.exit(1)
        return benchmark_ids

    output_paths = pipe(
        list(benchmark_id) + [make_id(read_yaml(x)) for x in result_yaml],
        unique,
        list,
        raise_error,
        map_(render_single(result_list, result_yaml, dest)),
        concat,
        list,
    )

    output(output_paths)


@curry
def render_single(result_list, result_yaml, dest, benchmark_id):
    """Render a single notebook

    Args:
       result_list: path to list of results
       result_yaml: path to the result meta file
       dest: the path to write the new notebook
       benchmark_id: the benchmark to render
    """

    return pipe(
        os.path.join(dest, f"result_list_{benchmark_id}.yaml"),
        make_tmp_list(result_list),
        add_list_items(list(map_(makeabs, result_yaml))),
        generate_notebook(
            pathlib.Path(__file__).parent.resolve() / ".." / "notebooks",
            dest,
            benchmark_id,
        ),
    )


@curry
def make_tmp_list(result_list, tmp_list_path):
    """Write the result list to the a temporary file

    Args:
      result_list: path or URL to the list of results
      tmp_list_path: temporary place to store and overwrite list

    Returns:
      the tmp_list_path

    """
    if result_list[0] is click_params.URL:
        return download_file(result_list[1], dest=tmp_list_path)

    shutil.copyfile(result_list[1], tmp_list_path)
    return tmp_list_path


@curry
def generate_notebook(nb_path, dest, benchmark_id, tmp_list_path):
    """Generate the notebook given various paths

    Args:
      nb_path: the local path to notebooks
      dest: the destination directory to write the new notebook
      benchmark_id: the benchmark ID
      tmp_list_path: the path to the results list

    Returns:
      the output path of the notebook
    """
    output_path = lambda x: os.path.join(dest, f"benchmark{x}.ipynb")
    pm.execute_notebook(
        nb_path / "template.ipynb",
        output_path(benchmark_id),
        parameters=assoc(
            read_yaml(nb_path / f"benchmark{benchmark_id}.yaml"),
            "benchmark_path",
            str(tmp_list_path),
        ),
        progress_bar=True,
    )
    return [output_path(benchmark_id), tmp_list_path]


@cli.command(epilog=EPILOG)
def test():  # pragma: no cover
    """Run the PFHub tests

    Currently creates a stray .coverage file when running.
    """
    pfhub_test()


@cli.command(epilog=EPILOG)
@click.argument(
    "file_path",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default="./pfhub.yaml",
)
@click.option("--sandbox/--no-sandbox", default=True)
def upload(file_path, sandbox):  # pylint: disable=unused-argument
    """Upload PFHub data to Zenodo"""
    url = upload_to_zenodo(file_path, sandbox)
    click.secho(message=f"Uploaded to {url}", fg="green")


@cli.command(epilog=EPILOG)
@click.argument("url", type=click_params.URL)
def submit(url):  # pylint: disable=unused-argument
    """(Not implemented) Submit to Zenodo and open PFHub PR"""


@cli.command(epilog=EPILOG)
def submit_from_zenodo():  # pylint: disable=unused-argument
    """(Not implemented) Submit an existing Zenodo record to PFHub"""


def zenodo_regexs():
    """Regular expression for acceptable Zenodo URLs"""
    return [
        r"https://doi.org/10.5281/zenodo.(\d{1,})",
        r"https://zenodo.org/api/records/(\d{1,})",
        r"https://zenodo.org/record/(\d{1,})",
    ]


def zenodo_sandbox_regexs():
    """Regular expression for acceptable Zenodo sandbox URLs"""
    return [
        r"https://sandbox.zenodo.org/record/(\d{1,})",
        r"https://sandbox.zenodo.org/api/records/(\d{1,})",
    ]


def get_zenodo_record_id(url, regexs):
    """Get the record from a Zenodo URL

    Args:
      url: any URL (doesn't need to be Zenodo)
      regexs: acceptable regexs

    Returns:
      Record ID or None
    """
    return pipe(
        regexs,
        map_(lambda x: re.fullmatch(x, url)),
        compact,
        map_(lambda x: x.groups()[0]),
        list,
        get(0, default=None),
    )


def validate_old_url(url):
    """Validate that a URL link against the old schema

    Args:
      url: the url for the file
    """
    tmpdir = tempfile.mkdtemp()
    name = get_name(url)
    dest = os.path.join(tmpdir, name)
    file_path = download_file(url, dest=dest)
    result = validate_old_(file_path)
    shutil.rmtree(tmpdir)
    return result


def validate_old_(path):
    """Validate a file against the old schema

    Args:
      path: the path to the file
    """
    schema_file = os.path.join(
        os.path.split(__file__)[0], "..", "schema", "schema_meta.yaml"
    )
    try:
        obj = pykwalify.core.Core(source_file=path, schema_files=[schema_file])
    except pykwalify.errors.CoreError:
        return False
    try:
        obj.validate(raise_exception=True)
    except pykwalify.errors.SchemaError:
        return False
    return True


def validate_(path):
    """Validate a YAML file against the new schema

    Uses linkml

    Args:
      path: path to the YAML file

    Returns:
      whether the schema is valid
    """
    schema_file = os.path.join(
        os.path.split(__file__)[0], "..", "schema", "pfhub_schema.yaml"
    )
    try:
        validator.cli.callback(path, None, None, schema=schema_file)
    except SystemExit as error:
        return error.code == 0
    except KeyError as error:
        print(f"KeyError: {error}")
        return False
    raise RuntimeError(
        "the linkml validator did not exit correctly"
    )  # pragma: no cover


def output(local_filepaths):
    """Output formatted file names with commas to stdout

    Args:
      local_filepaths: list of file path strings
    """

    def echo(local_filepath, newline, comma=","):
        formatted_path = click.format_filename(local_filepath)
        click.secho(message=f" {formatted_path}" + comma, fg="green", nl=newline)

    click.secho(message="Writing:", fg="green", nl=False)
    for local_filepath in local_filepaths[:-1]:
        echo(local_filepath, False)
    echo(local_filepaths[-1], True, comma="")
