"""Console API for copyrite."""

import concurrent.futures
import fnmatch
import json
import os

import click

from copyrite import file_copyrights
from copyrite import alias
from copyrite.vcs import KNOWN_BACKENDS


_COPYRIGHT_HEADER_MARKS = [
    b"# Copyright (c)",
    b"# copyright ",
    b"# Copyright ",
]


def _has_encoding_cookie(line):
    return line.startswith(b"# -*- coding")


def _has_non_ascii_characters(lines):
    for line in lines:
        try:
            line.decode('ascii')
        except UnicodeDecodeError:
            return True
    return False


def insert_copyrights(copyrights, lines, process_missing=False):
    """Insert the given copyrights into the known lines

    This operation will find the proper place where the copyrights
    can live, by replacing the current copyrights notices, if any.
    If *process_missing* is set to True, then the copyrights can
    be added, even if the lines don't contain any copyright notice.
    It also handles the case of encoding cookies, if the copyrights
    contain non ASCII characters.
    """
    has_cookie = _has_encoding_cookie(lines[0])
    copyright_indexes = [index for (index, line) in enumerate(lines)
                         if any(line.startswith(header) for header in _COPYRIGHT_HEADER_MARKS)]
    extraheader = []

    if not copyright_indexes:
        if not process_missing:
            return lines

        # Default to beginning of file.
        if has_cookie:
            lines = lines[0:1] + copyrights + lines[1:]
        else:
            lines = copyrights + lines
    else:
        index = copyright_indexes[0]

        if _has_non_ascii_characters(copyrights):
            if not has_cookie:
                extraheader = [b"# -*- coding: utf-8 -*-\n"]

        lines = lines[:index] + copyrights + lines[index + len(copyright_indexes):]
    return extraheader + lines


def _write_directory_copyrights(contribution_threshold, change_threshold,
                                backend, jobs,
                                include, exclude,
                                aliases,
                                process_missing,
                                directory):

    def _write_to_file_cb(future):
        nonlocal futures

        file_path = futures[future]
        copyrights = future.result()

        copyrights = [copyright + b"\n" for copyright in copyrights]

        with open(file_path, 'rb') as stream:
            lines = stream.readlines()

        if not lines:
            return

        lines = insert_copyrights(copyrights, lines, process_missing)

        with open(file_path, 'wb') as stream:
            stream.write(b"".join(lines))


    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {}
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)

                if include and not fnmatch.fnmatch(filepath, include):
                    continue
                if exclude and fnmatch.fnmatch(filepath, exclude):
                    continue

                future = executor.submit(
                    file_copyrights,
                    dirpath, filename, backend,
                    change_threshold,
                    contribution_threshold,
                    aliases)
                future.add_done_callback(_write_to_file_cb)
                futures[future] = filepath

        print("Start processing files..")
        concurrent.futures.wait(futures)
        print("Done!")


def _build_aliases_from_file(aliases):
    with aliases:
        content = json.load(aliases)
    return alias.build_from_json(content)


@click.command()
@click.option('--contribution-threshold', default=1,
              help='Number of contributions an user should have in '
                   'order to be considered')
@click.option('--change-threshold', default=10,
              help='Number of lines an user should have edited '
                   'in a file in order for the contribution to be '
                   'considered')
@click.option('--backend-type', required=True,
              type=click.Choice(KNOWN_BACKENDS.keys()))
@click.option('--jobs', type=int, default=1,
              help='Parallel jobs for processing the files')
@click.option('--include', type=str, default='*.py',
              help='Include only the files which are matched '
                   'by this glob pattern.')
@click.option('--exclude', type=str,
              help='Exclude the files which are matched '
                   'by this glob pattern. The exclusion '
                   'is done on the included files.')
@click.option('--aliases', type=click.File('r'),
              help='File containing name aliases.')
@click.option('--process-missing', type=bool, default=False,
              help='Add a copyright notice to files which do not '
                   'have them.')
@click.argument('directory')
def main(contribution_threshold,
         change_threshold,
         backend_type,
         jobs,
         include,
         exclude,
         aliases,
         process_missing,
         directory):
    """Console script for copyrite"""
    if aliases:
        built_aliases = _build_aliases_from_file(aliases)
    else:
        built_aliases = []

    backend = KNOWN_BACKENDS[backend_type]()
    _write_directory_copyrights(contribution_threshold,
                                change_threshold,
                                backend, jobs,
                                include, exclude,
                                built_aliases,
                                process_missing,
                                directory)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter; click too dynamic
    main()
