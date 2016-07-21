from copyrite import copyrite
from copyrite.vcs import ChangeDiff

import test


def test_is_significant_change():
    good_diff = ChangeDiff([1, 2, 3], [0, 0, 0])

    assert copyrite.is_significant_change(good_diff,
                                          positive_threshold=1)

    assert not copyrite.is_significant_change(good_diff,
                                              positive_threshold=4)
