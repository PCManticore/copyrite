from copyrite import cli


def test_insert_in_missing_without_cookies():
    lines_without_copyright = [b'Something']
    copyrights = [b'Working']

    lines = cli.insert_copyrights(copyrights, lines_without_copyright,
                                  process_missing=True)

    assert lines == copyrights + lines_without_copyright


def test_insert_in_missing_with_cookies():
    lines_without_copyright = [b'# -*- coding: utf-8 -*-', b'Something']
    copyrights = [b'Working']

    lines = cli.insert_copyrights(copyrights, lines_without_copyright,
                                  process_missing=True)

    assert lines == lines_without_copyright[0:1] + copyrights + lines_without_copyright[1:]


def test_do_not_insert_in_missing():
    lines_without = [b"first"]
    lines = cli.insert_copyrights([], lines_without)

    assert lines == lines_without


def test_with_copyrights_and_no_cookie():
    lines_with_copyright = [b"# Copyright (c) 2014 Google", b"first", b"second"]
    copyrights = [b"# Copyright (c) 2015 Goog\xa3"]

    lines = cli.insert_copyrights(copyrights, lines_with_copyright)

    expected = [b"# -*- coding: utf-8 -*-\n"] + copyrights + lines_with_copyright[1:]
    assert lines == expected


def test_with_copyrights():
    lines_with_copyright = [b"# Copyright (c) 2014 Google", b"first", b"second"]
    copyrights = [b"works"]

    lines = cli.insert_copyrights(copyrights, lines_with_copyright)

    assert lines == copyrights + lines_with_copyright[1:]


def test_with_copyrights_without_c():
    lines_with_copyright = [b"# Copyright 2014 Google", b"first", b"second"]
    copyrights = [b"works"]

    lines = cli.insert_copyrights(copyrights, lines_with_copyright)

    assert lines == copyrights + lines_with_copyright[1:]
