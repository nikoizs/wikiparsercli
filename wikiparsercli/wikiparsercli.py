#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: wikiparsercli.py
#
# Copyright 2021 Niko Izsak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for wikiparsercli.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
import logging.config
import json
import argparse
import coloredlogs
from wikiparserlib import WikipediaSeries


__author__ = '''Niko Izsak <izsak.niko@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''28-02-2021'''
__copyright__ = '''Copyright 2021, Niko Izsak'''
__credits__ = ["Niko Izsak"]
__license__ = '''MIT'''
__maintainer__ = '''Niko Izsak'''
__email__ = '''<izsak.niko@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''wikiparsercli'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def get_arguments():
    """
    Gets us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='''A cli tool for the wiki parser library''')
    parser.add_argument('--log-config',
                        '-l',
                        action='store',
                        dest='logger_config',
                        help='The location of the logging config json file',
                        default='')
    parser.add_argument('--log-level',
                        '-L',
                        help='Provide the log level. Defaults to info.',
                        dest='log_level',
                        action='store',
                        default='info',
                        choices=['debug',
                                 'info',
                                 'warning',
                                 'error',
                                 'critical'])
    parser.add_argument('--name', '-n',
                        dest='series_name',
                        action='store',
                        help='The series name you want to search for',
                        type=str,
                        required=True)

    args = parser.parse_args()
    return args


def setup_logging(level, config_file=None):
    """
    Sets up the logging.

    Needs the args to get the log level supplied

    Args:
        level: At which level do we log
        config_file: Configuration to use

    """
    # This will configure the logging, if the user has set a config file.
    # If there's no config file, logging will default to stdout.
    if config_file:
        # Get the config for the logger. Of course this needs exception
        # catching in case the file is not there and everything. Proper IO
        # handling is not shown here.
        try:
            with open(config_file) as conf_file:
                configuration = json.loads(conf_file.read())
                # Configure the logger
                logging.config.dictConfig(configuration)
        except ValueError:
            print(f'File "{config_file}" is not valid json, cannot continue.')
            raise SystemExit(1)
    else:
        coloredlogs.install(level=level.upper())


def main():
    """
    Main method.

    This method holds what you want to execute when
    the script is run on command line.
    """
    args = get_arguments()
    setup_logging(args.log_level, args.logger_config)
    if args.series_name:
        LOGGER.info("seacrching for {}".format(args.series_name))
        series = WikipediaSeries()
        results = series.search_by_name(args.series_name)
        found_match = series.check_for_match_in_result(results)
        if not found_match:
            for idx, search_result in enumerate(results):
                LOGGER.info('{}:{}'.format(idx, search_result.title))
            user_choice = int(input("Found multiple results, please choose the correct one:"))
            if results[user_choice]:
                LOGGER.debug("You chose: {}".format(results[user_choice].title))
                found_match = series.check_for_match_in_result([results[user_choice]])
        soup = series.get_soup_by_url(found_match.url)
        series.parse_series_title_and_type(found_match)
        is_miniseris = True if found_match.query_type == 'miniseries' else False
        series.parse_seasons_and_episodes_from_soup(soup, miniseries=is_miniseris)
        series.write_to_file_system()
if __name__ == '__main__':
    main()
