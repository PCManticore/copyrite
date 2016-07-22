"""Package which contains implementations of the needed functionality for various vcses."""

from .base import Contribution, ChangeDiff, VCSBackend
from .git import GitBackend

KNOWN_BACKENDS = {
    'git': GitBackend
}
