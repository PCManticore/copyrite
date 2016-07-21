from copyrite import alias
from copyrite.vcs import Contribution

import pytest


@pytest.fixture
def contributions():
    return [
        Contribution('John', 'john@xyz.com', 2013, None, None),
        Contribution('Josh', 'josh@zyx.com', 2014, None, None),
        Contribution('Mika', 'mika@abc.com', 2015, None, None),
        Contribution('Vic', 'vic@abc.com', 2016, None, None),
        Contribution('Lana', 'lana@xyz.com', 2017, None, None)
    ]


@pytest.fixture
def aliases():
    return [
        alias.Alias('XYZ', ['josh@zyx.com', 'lana@xyz.com']),
        alias.Alias('ABC', ['john@xyz.com', 'mika@abc.com', 'vic@abc.com'], 'a@abc.com')
    ]


def test_no_candidate_replaced(contributions):
    transformed = alias.apply_aliases(contributions, [])

    assert sorted(transformed) == sorted(contributions)


def test_candidates_replaced(aliases, contributions):
    transformed = sorted(alias.apply_aliases(contributions, aliases))

    assert len(transformed) == 5
    xyz = [contribution for contribution in transformed if contribution.author == 'XYZ']
    abc = [contribution for contribution in transformed if contribution.author == 'ABC']

    assert len(xyz) == 2
    assert len(abc) == 3
    assert all(contribution.mail == 'a@abc.com' for contribution in abc)
