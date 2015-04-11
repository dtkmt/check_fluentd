#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import urllib2
# import json
from optparse import OptionParser

parser = OptionParser()

parser.add_option(
    "-u", "--url",
    default="localhost:24420",
    type="string",
    help="Fluentd monitor_agent URL (default: localhost:24420)",
    dest="url")

(options, args) = parser.parse_args()

print options

