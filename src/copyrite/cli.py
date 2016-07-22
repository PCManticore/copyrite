"""Console API for copyrite."""

import concurrent.futures
import fnmatch
import json
import os

import click

from copyrite import file_copyrights
from copyrite import alias
from copyrite.vcs import KNOWN_BACKENDS


_COPYRIGHT_HEADER_MARK = b"# Copyright (c)"


def _write_directory_copyrights(contribution_threshold, change_threshold,
                                backend, jobs,
                                include, exclude,
                                aliases,
                                directory):

    def _write_to_file_cb(future):
        nonlocal futures

        file_path = futures[future]
        copyrights = future.result()
        copyrights = [copyright + b"\n" for copyright in copyrights]

        with open(file_path, 'rb') as stream:
            lines = stream.readlines()
        copyright_indexes = [index for (index, line) in enumerate(lines)
                             if line.startswith(_COPYRIGHT_HEADER_MARK)]
        if not copyright_indexes:
            # TODO: Do not process files without copyright?
            return

        index = copyright_indexes[0]
        lines = lines[:index] + copyrights + lines[index + len(copyright_indexes):]

        with open(file_path, 'wb') as stream:
            # TODO: detect newlines
            stream.write(b"".join(lines))


    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {}
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)

                if not fnmatch.fnmatch(filepath, include):
                    continue
                if fnmatch.fnmatch(filepath, exclude):
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
@click.option('--exclude', type=str, default='*test*',
              help='Exclude the files which are matched '
                   'by this glob pattern. The exclusion '
                   'is done on the included files.')
@click.option('--aliases', type=click.File('r'),
              help='File containing name aliases.')
@click.argument('directory')
def main(contribution_threshold,
         change_threshold,
         backend_type,
         jobs,
         include,
         exclude,
         aliases,
         directory):
    """Console script for copyrite"""

    built_aliases = _build_aliases_from_file(aliases)
    backend = KNOWN_BACKENDS[backend_type]()
    _write_directory_copyrights(contribution_threshold,
                                change_threshold,
                                backend, jobs,
                                include, exclude,
                                built_aliases, directory)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter; click too dynamic
    main()
