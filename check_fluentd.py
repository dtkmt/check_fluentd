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

DEFAULT_LIMIT = 17

parser = OptionParser()
parser.add_option(
    "-u", "--url", default="localhost:24220", type="string",
    help="Fluentd monitor_agent URL (default: localhost:24220)",
    dest="url")
parser.add_option(
    "-w", "--warning", default=5, type="int",
    help="warning threthold (default: retry_limit - 5)",
    dest="warn")
parser.add_option(
    "-c", "--critical", default=3, type="int",
    help="critical threthold (default: retry_limit - 3)",
    dest="crit")
parser.add_option(
    "-p", "--print", action="store_true", dest="printflg",
    help="Show parsed Fluentd metrics")
(options, args) = parser.parse_args()


def getMetrics():
    url = "http://" + options.url + "/api/plugins.json"
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    results = json.loads(f.read())
    return results['plugins']


def print_metrics():
    results = getMetrics()
    for result in results:
        print json.dumps(result, indent=4, sort_keys=True)
    sys.exit(STATUS_OK)


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


def set_threthold(result, threthold, flg):
    if flg == "WARN":
        if 'retry_limit' in result['config']:
            threthold = int(result['config']['retry_limit']) - options.warn
        else:
            threthold = DEFAULT_LIMIT - options.warn
    else:
        if 'retry_limit' in result['config']:
            threthold = int(result['config']['retry_limit']) - options.crit
        else:
            threthold = DEFAULT_LIMIT - options.crit
    return threthold


def varidate_metrics(results):
    for result in results:
        if result['retry_count'] is not None:
            return None
    print "UNKNOWN: retry_count metric does not exist."
    sys.exit(STATUS_UNKNOWN)


def main():
    results = getMetrics()
    if options.printflg:
        print_metrics()
    varidate_metrics(results)
    for result in results:
        warn = set_threthold(result, options.warn, "WARN")
        crit = set_threthold(result, options.crit, "CRIT")
        checkCount(result['retry_count'], warn, crit)

if __name__ == '__main__':
    main()
