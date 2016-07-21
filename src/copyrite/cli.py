"""Console API for copyrite."""

import concurrent.futures
import fnmatch
import os

import click

from copyrite import file_copyrights
from copyrite.vcs import KNOWN_BACKENDS


def _directory_copyrights(contribution_threshold, change_threshold,
                          backend, jobs,
                          include, exclude, directory):
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {}
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)

                if not fnmatch.fnmatch(filepath, include):
                    continue
                if fnmatch.fnmatch(filepath, exclude):
                    continue

                futures[executor.submit(
                    file_copyrights,
                    dirpath, filename, backend,
                    change_threshold,
                    contribution_threshold,
                    []) # TODO: aliases
                ] = filepath

        for completed in concurrent.futures.as_completed(futures):
            filepath = futures[completed]
            copyrights = completed.result()
            yield filepath, copyrights



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
@click.argument('directory')
def main(contribution_threshold,
         change_threshold,
         backend_type,
         jobs,
         include,
         exclude,
         directory):
    """Console script for copyrite"""
    backend = KNOWN_BACKENDS[backend_type]()
    for filepath, copyrights in _directory_copyrights(contribution_threshold,
                                                      change_threshold,
                                                      backend, jobs,
                                                      include, exclude, directory):
        print(filepath, copyrights)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter; click too dynamic
    main()
