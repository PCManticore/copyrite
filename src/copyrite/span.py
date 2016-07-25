"""Defines a class for handling contributions and their spans."""

import collections
from typing import List, Optional


ContributionSpan = collections.namedtuple('ContributionSpan', 'author mail dates')
_COPYRIGHT_HEADER = b"# Copyright (c) %s %s"


def _format_spans(spans: List[List[int]]) -> str:
    ordered = sorted(spans)
    formatted = []
    for span in ordered:
        if len(span) == 1:
            formatted.append(str(span[0]))
        else:
            head, tail = span[0], span[-1]
            formatted.append("{}-{}".format(head, tail))
    return ", ".join(formatted)


def format_span(span: ContributionSpan,
                # pylint: disable=bad-whitespace; fp..
                copyright_header: Optional[str] = None) -> bytes:
    """Format this contributions into a format suitable for files."""
    if copyright_header is not None:
        header = copyright_header.encode()
    else:
        header = _COPYRIGHT_HEADER

    if span.mail:
        author = b"%s <%s>" % (span.author, span.mail)
    else:
        author = span.author
    formatted_spans = _format_spans(span.dates).encode()
    return header % (formatted_spans, author) # type: ignore; fp
