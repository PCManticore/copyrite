"""Backend for the git vcs."""

import datetime
import subprocess
import typing

from . import base


def _year_from_date(date: bytes) -> int:
    return datetime.datetime.strptime(date.decode(), "%Y-%m-%d").year


class GitBackend(base.VCSBackend):
    """Backend for the git vcs."""

    @property
    def executable(self):
        return 'git'

    @staticmethod
    def _parse_log_line(line: bytes, filename: str) -> base.Contribution:
        name, mail, date, change = line.split(b'##')
        year = _year_from_date(date)
        return base.Contribution(name, mail, year, change.decode(), filename)

    @staticmethod
    def _raw_line_parse(command: typing.List[str],
                        vcs_directory: str) -> typing.List[bytes]:

        popen = subprocess.Popen(command, cwd=vcs_directory,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        out, _ = popen.communicate()
        return out.splitlines()

    def _log_command(self, filename):
        return [self.executable, 'log', '--follow', '--format="%an##%ae##%ad##%H"',
                '--date=short', filename]

    def _change_command(self, change, filename):
        return [self.executable, 'show', '--format=oneline', change, filename]

    def _raw_file_logs(self, filename: str, vcs_directory: str) -> typing.List[bytes]:
        command = self._log_command(filename)
        return self._raw_line_parse(command, vcs_directory)

    def _raw_file_change(self, filename: str,
                         change: str,
                         vcs_directory: str) -> typing.List[bytes]:

        command = self._change_command(change, filename)
        return self._raw_line_parse(command, vcs_directory)

    def file_contributions(self, filename: str, directory: str) -> typing.List[base.Contribution]:
        """Get a list of contributions for the given file."""

        raw_lines = self._raw_file_logs(filename, directory)
        logs = [self._parse_log_line(line[1:-1], filename) for line in raw_lines]
        return list(filter(None, logs))

    def contribution_changes(self, contribution: base.Contribution,
                             directory: str) -> base.ChangeDiff:
        """Get a ChangeDiff object from a given contribution."""

        raw_lines = self._raw_file_change(contribution.filename,
                                          contribution.hash,
                                          directory)
        positive = []
        negative = []
        for line in raw_lines:
            if line.startswith(b'+'):
                positive.append(line)
            elif line.startswith(b'-'):
                negative.append(line)
        return base.ChangeDiff(positive, negative)
        