#
# linter.py
# Linter for SublimeLinter4, a code checking framework for Sublime Text 3
#
# Written by Markus Liljedahl
# Copyright (c) 2017 Markus Liljedahl
#
# License: MIT
#

"""This module exports the AnsibleLint plugin class."""
import re
import logging
from SublimeLinter.lint import Linter, util
logger = logging.getLogger('SublimeLinter.plugin.ansbile-lint')


class AnsibleLint(Linter):
    """Provides an interface to ansible-lint."""

    # ansbile-lint verison requirements check
    version_args = '--version'
    version_re = r'(?P<version>\d+\.\d+\.\d+)'
    version_requirement = '>= 3.0.1'

    # linter settings
    cmd = ('ansible-lint', '${args}', '${file}')
    regex = r'^.+:(?P<line>\d+): \[.(?P<error>.+)\] (?P<message>.+)'
    # -p generate non-multi-line, pep8 compatible output
    multiline = False

    # ansible-lint does not support column number
    word_re = False
    line_col_base = (1, 1)

    tempfile_suffix = 'yml'
    error_stream = util.STREAM_STDOUT

    defaults = {
        'selector': 'source.ansible',
        'args': '--nocolor -p',
        '--exclude= +': ['.galaxy'],
        '-c': '',
        '-r': '',
        '-R': '',
        '-t': '',
        '-x': '',
    }
    inline_overrides = ['c', 'exclude', 'r', 'R', 't', 'x']

    def find_errors(self, output):
        """Parse errors from linter's output.

        Display only errors for matching file
        ansible-lint parses given playbook and its dependent roles

        TODO: add ansible dependencies, so that we detect playbooks and then
        iterate over them to detect if given open file belongs to the role
        included in the playbook
        if yes, then run ansible-lint on those playbooks and process output
        """
        pattern = r'^{}(.*)'.format(re.escape(self.filename))

        for line in output.splitlines():

            # filter out lines which do not match currently opened file
            out = re.match(pattern, line)
            if not out:
                continue

            found = self.regex.match(line.rstrip())
            if found:
                yield self.split_match(found)
            else:
                logger.info(
                    "{}: No match for line: '{}'".format(self.name, line))
