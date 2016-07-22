===============================
copyrite
===============================


.. image:: https://img.shields.io/pypi/v/copyrite.svg
        :target: https://pypi.python.org/pypi/copyrite

.. image:: https://img.shields.io/travis/PCManticore/copyrite.svg
        :target: https://travis-ci.org/PCManticore/copyrite

.. image:: https://pyup.io/repos/github/PCManticore/copyrite/shield.svg
     :target: https://pyup.io/repos/github/PCManticore/copyrite/
     :alt: Updates


Updates copyright notices.


* Free software: MIT license
* Documentation: https://copyrite.readthedocs.io.


About
=====

This is a short tool I've built for handling missing copyright
notices in my open source projects (mostly pylint_ and astroid_).
The problem was that the copyright notices were too coarse,
belonging only to the initial author of those two projects (Logilab),
which stopped contributing that much in the past years. Since some
contributors weren't willing to rennounce the copyright for a
commercial entity, we found the need of a tool for updating the
copyright notices across the board in order to reflect the reality
of the contributions from the last year.

**copyrite** is extremely simple: it just need a repository
and, driven by a couple of options, it goes into each file and
replaces the copyright notices it finds with more up-to-date notices.

Features
--------

   * `concurrent`. You can use the ``--jobs`` flag for controlling
     the number of processes it should use for processing your file.
     Defaults to 1.

   * `backend generic`. It could support multiple VCSes easily,
     although right now it has only ``git`` support.

   * supports aliases

     If a contributor used multiple emails for contributing to a project,
     you can use the ``--aliases`` option. It requires a JSON file with
     a certain structure, as seen below.

     Each entry in the alias should be a dictionary, containing two
     required fields, ``mails`` and ``name`` and one optional field,
     ``authoritative_mail``.

     If the ``authoritative_mail`` is not given, the generated copyright
     will look as in::

         # Copyright (c) {year_span} {name}

     If the ``authoritative_name`` is given, then this will look as::

         # Copyright (c) {year_span} {name} <{mail}>

     The ``year_span`` represents the years in which a contributor
     made their contributions to that particular file.

     .. code-block:: js

         [
           {
             "mails": [
               "cpopa@cloudbasesolutions.com"
             ],
             "authoritative_mail": "ala@bala.com",
             "name": "Claudiu Popa"
           },
           {
             "mails": [
               "george@oops.com"
             ],
             "name": "Oops",
           },
         ]

   * supports thresholds for contributions

     There are two flags which control how a contribution should be
     considered. ``--contribution-threshold`` is specifying how many
     commits a contributor should have for a file in order for the
     contributions to be taken in consideration.
     ``--change-threshold`` specifies what is the least amount of
     added lines that a change should have. These two are exclusive,
     which means that a change threshold of 100 can have more
     importance than a contribution threshold of 2.


And here is an example::

    $ copyrite --contribution-threshold 10 --change-threshold 4 --backend-type git my_repo --aliases=aliases_file


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _pylint: https://github.com/PyCQA/pylint
.. _astroid: https://github.com/PyCQA/astroid)
