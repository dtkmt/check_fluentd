#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import sys
from optparse import OptionParser

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

RETRY_LIMIT = 17

parser = OptionParser()
parser.add_option(
    "-u", "--url", default="localhost:24220", type="string",
    help="Fluentd monitor_agent URL (default: localhost:24220)",
    dest="url")
parser.add_option(
    "-w", "--warning", default=None, type="int",
    help="warning threthold (default: retry_count - 5)",
    dest="warn")
parser.add_option(
    "-c", "--critical", default=None, type="int",
    help="critical threthold (default: retry_count - 3)",
    dest="crit")
(options, args) = parser.parse_args()


def getMetrics():
    url = "http://" + options.url + "/api/plugins.json"
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    results = json.loads(f.read())
    return results['plugins']


def checkCount(count, warning, critical):
    if count is not None:
        if count >= critical:
            print "CRITICAL: retry_count is %d, crit:%d" % (count, critical)
            sys.exit(STATUS_CRITICAL)
        if count >= warning:
            print "WARNING: retry_count is %d, warn:%d" % (count, warning)
            sys.exit(STATUS_WARNING)
        else:
            print "OK: retry_count is %d" % (count)
            sys.exit(STATUS_OK)


def set_warn_threthold(result, threthold):
    if threthold is None:
        if 'retry_limit' in result['config']:
            retry_limit = result['config']['retry_limit']
            threthold = int(retry_limit) - 3
        else:
            threthold = RETRY_LIMIT - 3
    return threthold


def set_crit_threthold(result, threthold):
    if threthold is None:
        if 'retry_limit' in result['config']:
            retry_limit = result['config']['retry_limit']
            threthold = int(retry_limit) - 5
        else:
            threthold = RETRY_LIMIT - 5
    return threthold


def main():
    results = getMetrics()
    for result in results:
        warn = set_warn_threthold(result, options.warn)
        crit = set_crit_threthold(result, options.crit)
        if 'retry_count' in result:
            checkCount(result['retry_count'], warn, crit)
        else:
            print "UNKNOWN: retry_count metric is None"
            sys.exit(STATUS_UNKNOWN)

if __name__ == '__main__':
    main()
