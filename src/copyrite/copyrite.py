"""copyrite - a tool for handling missing copyright attributions in a project's files."""

import collections
import itertools
from typing import Dict, List, Iterable, Tuple, Set

from copyrite import alias
from copyrite import span
from copyrite import vcs

# List of mails for which the contributions should be ignored.
_BLACKLIST_MAILS = [b"none@none"]


# pylint: disable=invalid-name
SpanList = List[span.ContributionSpan]
SpanIterable = Iterable[span.ContributionSpan]
AuthorToDate = Dict[Tuple[str, str], Set[int]]
AuthorContributions = Dict[str, List[vcs.Contribution]]
# pylint: enable=invalid-name


def _spans(dates):
    """Get the consecutive spans from the given dates."""
    spans = []
    current_span = []
    prev = 0
    for date in dates:
        if date == prev + 1:
            current_span.append(date)
        else:
            spans.append(list(current_span))
            current_span.clear()
            current_span.append(date)
        prev = date
    spans.append(current_span)
    return list(filter(None, spans))


def is_significant_change(change: vcs.ChangeDiff,
                          positive_threshold: int) -> bool:
    """Check if the given change can be considered significant

    A change is considered significant if the number of added lines
    is above a given level, which means that a small typo will
    probably not make a change be considered significant.
    """
    return len(change.positive) >= positive_threshold


def _contribution_spans(author_contributions: AuthorToDate) -> SpanIterable:
    for (author, mail), dates in author_contributions.items():
        ordered = sorted(set(dates))
        yield span.ContributionSpan(author, mail, _spans(ordered))


def contribution_spans(contributions: List[vcs.Contribution]) -> SpanList:
    """Get the span contributions from the given contributions

    The span contribution is an object with the author, author's mail and
    the dates when an author contributed to the project.
    """

    grouper = itertools.groupby(contributions, lambda con: (con.author, con.mail))
    spans = collections.defaultdict(set) # type: AuthorToDate
    for author_mail, group in grouper:
        spans[author_mail].update(con.date for con in group)
    return list(_contribution_spans(spans))


def significant_changes(changes: List[vcs.ChangeDiff],
                        change_positive_threshold: int,
                        contributions_threshold: int) -> bool:
    """Check if the given changes are significant (usually for an author)."""
    has_enough_contributions = len(changes) >= contributions_threshold
    has_significant_contributions = any(
        is_significant_change(change, change_positive_threshold)
        for change in changes
    )
    return has_enough_contributions or has_significant_contributions


def _contributions_grouped_by_author(
        contributions: List[vcs.Contribution]) -> AuthorContributions:

    authors = collections.defaultdict(list) # type: AuthorContributions
    grouper = itertools.groupby(contributions,
                                lambda con: con.author)
    for author, group in grouper:
        authors[author].extend(list(group))
    return authors


def _significant_contributions(authors: AuthorContributions,
                               backend: vcs.VCSBackend,
                               dirpath: str,
                               change_positive_threshold: int,
                               contributions_threshold: int) -> Iterable[List[vcs.Contribution]]:

    for author_contributions in authors.values():
        changes = [backend.contribution_changes(contribution, dirpath)
                   for contribution in author_contributions]

        if significant_changes(changes, change_positive_threshold, contributions_threshold):
            yield author_contributions


def file_copyrights(directory: str,
                    filepath: str,
                    backend: vcs.VCSBackend,
                    change_positive_threshold: int,
                    contributions_threshold: int,
                    aliases: List[alias.Alias]) -> List[span.ContributionSpan]:

    """Generate a list of Copyright notices for the given file."""

    contributions = backend.file_contributions(filepath, directory)
    transformed_contributions = alias.apply_aliases(contributions, aliases)
    authors = _contributions_grouped_by_author(transformed_contributions)
    author_contributions = _significant_contributions(
        authors, backend, directory,
        change_positive_threshold,
        contributions_threshold)

    def _order_cb(item):
        return sorted(item.dates)[0][0]

    unflattened = [span for spans in map(contribution_spans, author_contributions)
                   for span in spans]
    filtered_spans = [span for span in unflattened
                      if span.mail not in _BLACKLIST_MAILS]
    return sorted(filtered_spans, key=_order_cb)
