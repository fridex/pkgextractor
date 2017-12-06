#!/usr/bin/env python3
"""Search for Python and RPM packages inside a Docker image."""

import contextlib
import json
import logging
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

import click
import daiquiri
import pyunpack

_LOGGER = daiquiri.getLogger(__name__)

_SELF_PATH = os.path.dirname(os.path.realpath(__file__))
_BIN_PATH = os.getenv('BINPATH', os.path.join(_SELF_PATH, 'bin'))
_MERCATOR_BIN = os.getenv('MERCATOR_BIN',
                          os.path.join(_SELF_PATH, _BIN_PATH, 'mercator'))
_MERCATOR_HANDLERS_YAML = os.getenv('MERCATOR_HANDLERS_YAML',
                                    os.path.join(_SELF_PATH, _BIN_PATH, 'handlers.yml'))
_CONTAINER_DIFF_BIN = os.getenv('CONTAINER_DIFF_BIN',
                                os.path.join(_SELF_PATH, _BIN_PATH, 'container-diff'))


class InputError(Exception):
    """Raised on invalid user input."""


def jsonify(dict_):
    """Convert a dictionary to JSON, do it in a pretty way.

    :param dict_: a dict that should be converted to a JSON
    :type dict_: dict
    :return: well-formatted JSON
    :rtype: str
    """
    return json.dumps(dict_, sort_keys=True, separators=(',', ': '), indent=2)


@contextlib.contextmanager
def tempdir():
    """Create a temporary file, delete it on leaving context."""
    dirpath = tempfile.mkdtemp()
    try:
        yield dirpath
    finally:
        if os.path.isdir(dirpath):
            _LOGGER.debug("Removing a temporary directory %r", dirpath)
            shutil.rmtree(dirpath)


def _run_command(cmd):
    """Run the given command and return its stdout.

    :param cmd: a string containing command that should be run
    :type cmd: str
    :rtype: str
    :return: stdout produced by the command
    :raises RuntimeError: signalizing process exited with non-zero value
    """
    _LOGGER.debug("Running command %r", cmd)
    try:
        output = subprocess.check_output(
            shlex.split(cmd),
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
    except subprocess.CalledProcessError as exc:
        _LOGGER.error(exc.stderr.replace('\\n', '\n'))
        err_msg = "Failed to run command %r" % cmd
        raise RuntimeError(err_msg) from exc
    return output


def _docker_save_image(image_name):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tar').name
    _LOGGER.debug("Saving docker image %r to an archive %r", image_name, temp_file)

    cmd = 'docker save {image_name} --output {temp_file}'.format(
        image_name=image_name,
        temp_file=temp_file
    )
    try:
        _run_command(cmd)
    except Exception:
        os.remove(temp_file)
        raise

    return temp_file


def _filter_container_diff_output(output):
    """Normalize and filter container-diff output."""
    result = []
    for entry in output[0].get('Analysis', []):
        result.append({'name': entry['Name'], 'version': entry['Version']})
    return result


def _filter_mercator_output(output):
    return output


def _run_container_diff_rpm(image_name, local=True):
    """Run container-diff tool to extract all installed RPM packages inside an image.

    :param image_name: name of image that should be analyzed
    :type image_name: str
    :param local: True if container-diff should contact local Docker daemon
    :type local: bool
    :return: information about installed RPM packages (names) with their corresponding version
    :rtype: dict
    """
    image = ('daemon://{0}' if local else 'remote://{0}').format(image_name)
    cmd = '{container_diff_bin} analyze --json --type rpm {image}'.format(
        container_diff_bin=_CONTAINER_DIFF_BIN,
        image=image
    )
    output = _run_command(cmd)
    return _filter_container_diff_output(json.loads(output))


def _run_mercator_pypi(path):
    """Run mercator-go to find all the PyPI packages that were installed inside an image.

    :param path: a path to extracted image filesystem
    :type path: str
    :return: all packages, version and path where packages were installed
    :rtype: dict
    """
    cmd = '{mercator_bin} -config {mercator_handlers_yaml} {path}'.format(
        mercator_bin=_MERCATOR_BIN,
        mercator_handlers_yaml=_MERCATOR_HANDLERS_YAML,
        path=path
    )
    output = _run_command(cmd)
    return json.loads(_filter_mercator_output(output))


def analyze(image_name=None, archive_path=None):
    """Search for installed PyPI and RPM packages inside a Docker image.

    :param image_name: name if the image to be analyzed (disjoint with archive_path)
    :type image_name: str
    :param archive_path: a path to stored archive (disjoint with image_name)
    :type archive_path: str
    :return: information about installed packages in the image
    :rtype: dict
    """
    if not image_name and not archive_path:
        raise InputError("Please specify archive path or image name that should be analyzed.")

    if image_name and archive_path:
        raise InputError("Options --archive-path and --image-name are disjoint")

    result = {
        'rpm': None,
        'pypi': None,
        'image_name': image_name
    }

    try:
        if image_name:
            archive_path = _docker_save_image(image_name)
            result['rpm'] = _run_container_diff_rpm(image_name)
        else:
            _LOGGER.warning("Collecting RPM packages on a local image archive not yet supported")

        with tempdir() as path:
            pyunpack.Archive(archive_path, backend='auto').extractall(path)
            result['pypi'] = _run_mercator_pypi(path)

    finally:
        if image_name:
            # There was specified an image name, clean a temporary archive.
            _LOGGER.debug("Cleaning temporary archive path %r", archive_path)
            os.remove(archive_path)

    return result


@click.group()
@click.option('-v', '--verbose', count=True,
              help='Level of verbosity, can be applied multiple times.')
def cli(verbose=0):
    """Package extraction from a Docker image."""
    # hack based on num values of logging.DEBUG, logging.INFO, ...
    level = max(logging.WARNING - verbose * 10, logging.DEBUG)
    daiquiri.setup(outputs=(daiquiri.output.STDERR,), level=level)


@cli.command('analyze')
@click.option('-i', '--image-name',
              help='Image name to be analyzed (disjoint with --archive-path).')
@click.option('-a', '--archive-path',
              help='Tar archive to be analyzed (disjoint with --image-name).')
@click.option('-o', '--output-file', type=click.File('w'),
              help='Store results in specified output file (defaults to stdout).')
def cli_analyze(image_name=None, archive_path=None, output_file=None):
    """Search for installed PyPI and RPM packages inside a Docker image."""
    output_file = output_file or sys.stdout
    result = analyze(image_name=image_name, archive_path=archive_path)
    output_file.write(jsonify(result))


if __name__ == '__main__':
    sys.exit(cli())
