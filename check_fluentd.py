#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import sys
from optparse import OptionParser

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
status_unknown = 3

parser = OptionParser()
parser.add_option(
    "-u", "--url", default="localhost:24220", type="string",
    help="Fluentd monitor_agent URL (default: localhost:24220)",
    dest="url")
parser.add_option(
    "-w", "--warning", default=None, type="int",
    help="warning threthold (default: 10)",
    dest="warn")
parser.add_option(
    "-c", "--critical", default=None, type="int",
    help="critical threthold (default: 15)",
    dest="crit")
(options, args) = parser.parse_args()


def getMetrics():
    url = "http://" + options.url + "/api/plugins.json"
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    results = json.loads(f.read())
    return results


def main():
    retry_limit = None
    warn = options.warn
    crit = options.crit
    results = getMetrics()
    for result in results['plugins']:
        if 'retry_limit' in result['config']:
            retry_limit = result['config']['retry_limit']
        if retry_limit is not None and (warn is None or crit is None):
            crit = int(retry_limit) - 3
            warn = int(retry_limit) - 5
        if 'retry_count' in result:
            count = result['retry_count']
            if count is not None:
                if count >= crit:
                    print "CRITICAL: retry_count is %d, crit:%d" % (count, crit)
                    sys.exit(STATUS_CRITICAL)
                if count >= warn:
                    print "WARNING: retry_count is %d, warn:%d" % (count, warn)
                    sys.exit(STATUS_WARNING)
                else:
                    print "OK: retry_count is %d" % (count)
                    sys.exit(STATUS_OK)
        else:
            print "UNKNOWN: retry_count metric is None"
            sys.exit(status_unknown)

if __name__ == '__main__':
    main()
