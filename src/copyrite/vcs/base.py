"""Base classes for the vcs subpackage."""

import abc
import collections
import typing


Contribution = collections.namedtuple('Contribution', 'author mail date hash filename')
ChangeDiff = collections.namedtuple('ChangeDiff', 'positive negative')


class VCSBackend(metaclass=abc.ABCMeta):
    """Backend for various VCSes

    We need this in order to interact with a repository,
    for retrieving file logs or contributions or whatnot.
    """

    @property
    @abc.abstractmethod
    def executable(self) -> str:
        """Define the executable of this VCS backend."""

    @abc.abstractmethod
    def file_contributions(self, filename: str, directory: str) -> typing.List[Contribution]:
        """Obtain the logs for the given filename."""

    @abc.abstractmethod
    def contribution_changes(self, contribution: Contribution, directory: str) -> ChangeDiff:
        """Get the changes that occurred in *change_hash*."""
