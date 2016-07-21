"""Console API for copyrite."""

import concurrent.futures
import os

import click

from copyrite import file_copyrights
from copyrite.vcs import KNOWN_BACKENDS


def _directory_copyrights(contribution_threshold, change_threshold,
                          backend, jobs, directory):
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {}
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                futures[executor.submit(
                    file_copyrights,
                    dirpath, filename, backend,
                    change_threshold,
                    contribution_threshold,
                    []) # TODO: aliases
                ] = os.path.join(dirpath, filename)

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
@click.argument('directory')
def main(contribution_threshold, change_threshold, backend_type, jobs, directory):
    """Console script for copyrite"""
    backend = KNOWN_BACKENDS[backend_type]()
    for filepath, copyrights in _directory_copyrights(contribution_threshold,
                                                      change_threshold,
                                                      backend, jobs, directory):
        print(filepath, copyrights)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter; click too dynamic
    main()
