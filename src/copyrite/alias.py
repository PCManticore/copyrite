"""Manages aliases for different authors."""

import collections
import typing

import jsonschema

from copyrite import vcs

_AliasBase = collections.namedtuple('_AliasBase', 'name mails authoritative_mail')
ALIAS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Aliases",
    "type": "array",
    "items": {
        "title": "Alias",
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "mails": {
                "type": "array",
                "items": {
                    "type": "string",
                    "properties": {
                        "mail": {
                            "type": "string"
                        }
                    }
                },
            },
            "authoritative_mail": {
                "type": "string",
            },
        },
        "required": ["name", "mails"]
    }
}


class Alias(_AliasBase):
    """An author alias

    An alias can be viewed as an authoritative entity under
    which multiple contributions can live. For instance,
    if one user contributed to the project by using multiple e-mails,
    the alias can be used to use only one of those names or another,
    prespecified name.
    """

    def __new__(cls,
                name: bytes,
                mails: typing.List[bytes],
                # pylint: disable=bad-whitespace; false positive
                authoritative_mail: typing.Optional[bytes] = None):

        return _AliasBase.__new__(cls, name, mails, authoritative_mail) # type: ignore; fp

    @classmethod
    def from_keys(cls, name: str,
                  mails: typing.List[str],
                  authoritative_mail: typing.Optional[str] = None): # pylint: disable=bad-whitespace
        """Build an alias from the given keys

        Since we are using bytes internally in order to not complicate
        ourselves with encodings and whatnot. We get bytes, we put
        bytes into files. The only exception is when we retrieve the
        aliases from a JSON file, which inherently contains strings.
        Thus the need for this method, which decodes those values
        into bytes before building the Alias object.
        """

        encoded_name = name.encode()
        encoded_mails = [mail.encode() for mail in mails] # type: List[bytes]
        encoded_authoritative_mail = authoritative_mail and authoritative_mail.encode()
        return cls(encoded_name, encoded_mails, encoded_authoritative_mail)


# pylint: disable=invalid-name
_ContributionsIterableType = typing.Iterable[vcs.Contribution]
_AliasContributionGroupType = typing.Dict[vcs.Contribution, Alias]
# pylint: enable=invalid-name


def _find_proper_alias(aliases: typing.List[Alias],
                       contribution: vcs.Contribution) -> typing.Optional[Alias]:

    for candidate_alias in aliases:
        if contribution.mail in candidate_alias.mails:
            # Valid candidate
            return candidate_alias


def _applied_aliases(candidates: _AliasContributionGroupType) -> _ContributionsIterableType:
    for contribution, alias in candidates.items():
        if alias:
            mail = alias.authoritative_mail or contribution.mail
            name = alias.name or contribution.author
            yield contribution._replace(author=name, mail=mail) # type: ignore
        else:
            yield contribution


def apply_aliases(contributions: typing.List[vcs.Contribution],
                  aliases: typing.List[Alias]) -> typing.List[vcs.Contribution]:
    """Apply the aliases over the contributions.

    The function finds all contributions which can live under a given alias
    and tries to apply the alias's information over them.
    """

    candidates = {contribution: _find_proper_alias(aliases, contribution)
                  for contribution in contributions}
    return list(_applied_aliases(candidates))


def build_from_json(aliases):
    """Build aliases from the given JSON structure.

    The structure should be valid according to the underlying schema.
    """
    jsonschema.validate(aliases, ALIAS_SCHEMA)
    return [Alias.from_keys(**alias) for alias in aliases]
