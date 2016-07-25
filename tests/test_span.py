from copyrite import span


def test_format_span_with_mail():
    contribution_span = span.ContributionSpan(
        b'test', b'something',
        [[2001, 2002], [2005, 2006, 2007, 2008]]
    )
    formatted = span.format_span(contribution_span)

    assert formatted == span._COPYRIGHT_HEADER % (
        b"2001-2002, 2005-2008", b"test <something>"
    )


def test_format_span_without_mail():
    contribution_span = span.ContributionSpan(
        b'test', b'',
        [[2001], [2005, 2006, 2007, 2008]]
    )
    formatted = span.format_span(contribution_span)

    assert formatted == span._COPYRIGHT_HEADER % (
        b"2001, 2005-2008", b"test"
    )


def test_format_span_copyright_header():
    contribution_span = span.ContributionSpan(
        b'test', b'something',
        [[2005, 2006, 2007, 2008], [2001]]
    )
    copyright_header = "works %s %s"
    formatted = span.format_span(contribution_span, copyright_header)

    assert formatted == copyright_header.encode() % (
        b"2001, 2005-2008", b"test <something>"
    )
