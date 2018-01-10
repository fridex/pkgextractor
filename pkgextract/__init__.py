#!/usr/bin/env python3
"""Search for Python and RPM packages inside a Docker image."""

import contextlib
import json
import os
import shlex
import subprocess
import tempfile

import daiquiri

_LOGGER = daiquiri.getLogger(__name__)

_MERCATOR_BIN = os.getenv('MERCATOR_BIN', 'mercator')
_MERCATOR_HANDLERS_YAML = os.getenv('MERCATOR_HANDLERS_YAML', '/usr/share/mercator/handlers.yml')
_CONTAINER_DIFF_BIN = os.getenv('CONTAINER_DIFF_BIN', 'container-diff')


@contextlib.contextmanager
def mount_image(image_name):
    """Mount a Docker image to a local filesystem."""
    dirpath = tempfile.mkdtemp()
    _LOGGER.debug("Mounting image %r to %r", image_name, dirpath)
    _run_command('atomic mount {image_name} {dirpath}'.format(
        image_name=image_name,
        dirpath=dirpath
    ))
    try:
        yield dirpath
    finally:
        _LOGGER.debug("Unmounting image %r from %r", image_name, dirpath)
        try:
            _run_command('atomic umount {dirpath}'.format(dirpath=dirpath))
        except:
            _LOGGER.exception("Failed to unmount image from {dirpath}".format(dirpath=dirpath))
            raise


def _run_command(cmd, env=None):
    """Run the given command and return its stdout.

    :param cmd: a string containing command that should be run
    :type cmd: str
    :param env: additional environment variables that should be supplied
    :type env: dict
    :type: str
    :return: stdout produced by the command
    :raises RuntimeError: signalizing process exited with non-zero value
    """
    _LOGGER.debug("Running command %r", cmd)
    try:
        output = subprocess.check_output(
            shlex.split(cmd),
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env
        )
    except subprocess.CalledProcessError as exc:
        _LOGGER.error(exc.output.replace('\\n', '\n'))
        err_msg = "Failed to run command %r" % cmd
        raise RuntimeError(err_msg) from exc
    return output


def _filter_container_diff_output(output):
    """Normalize and filter container-diff output."""
    result = []
    for entry in output[0].get('Analysis', []):
        result.append({
            'name': entry['Name'],
            'version': entry['Version']
        })
    return result


def _filter_mercator_output(output):
    """Normalize and filter mercator output."""
    for entry in output.get('items', []):
        entry.pop('digests', None)
        entry.pop('time', None)
    return output.get('items', [])


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
    return json.loads(output)


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
    output = _run_command(cmd, env={'MERCATOR_INTERPRET_SETUP_PY': 'true'})
    return json.loads(output)


def analyze(image_name):
    """Search for installed PyPI and RPM packages inside a Docker image.

    :param image_name: name if the image to be analyzed (disjoint with archive_path)
    :type image_name: str
    :return: information about installed packages in the image
    :rtype: dict
    """
    rpm_packages = _filter_container_diff_output(_run_container_diff_rpm(image_name))

    with mount_image(image_name) as path:
        pypi_packages = _filter_mercator_output(_run_mercator_pypi(path))

    return {
        'rpm': rpm_packages,
        'pypi': pypi_packages,
        'image_name': image_name
    }

