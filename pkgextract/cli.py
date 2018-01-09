#!/usr/bin/env python3
"""Implementation of CLI for pkgextract."""

import logging
import sys

import click
import daiquiri

from pkgextract import analyze


@click.group()
@click.option('-v', '--verbose', count=True,
              help='Level of verbosity, can be applied multiple times.')
def cli(verbose=0):
    """Package extraction from a Docker image."""
    # hack based on num values of logging.DEBUG, logging.INFO, ...
    level = max(logging.WARNING - verbose * 10, logging.DEBUG)
    daiquiri.setup(outputs=(daiquiri.output.STDERR,), level=level)


@cli.command('analyze')
@click.option('-i', '--image-name', required=True,
              help='Image name to be analyzed.')
@click.option('-o', '--output-file', type=click.File('w'),
              help='Store results in specified output file (defaults to stdout).')
def cli_analyze(image_name=None, output_file=None):
    """Search for installed PyPI and RPM packages inside a Docker image."""
    output_file = output_file or sys.stdout
    result = analyze(image_name)
    output_file.write(jsonify(result))
