#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import re
import sys
from optparse import OptionParser

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

DEFAULT_LIMIT = 17
DEFAULT_CHUNK_LIMIT = 8388608
DEFAULT_QUEUE_LIMIT = 256

parser = OptionParser()
parser.add_option(
    "-u", "--url", default="localhost:24220", type="string",
    help="Fluentd monitor_agent URL (default: localhost:24220)",
    dest="url")
parser.add_option(
    "-w", "--warning", default=5, type="int",
    help="Warning threshold retry_count (default: 5 (retry_limit - warn))",
    dest="warn")
parser.add_option(
    "-c", "--critical", default=3, type="int",
    help="Critical threshold retry_count (default: 3 (retry_limit - crit))",
    dest="crit")
parser.add_option(
    # "-W", "--buffer-warning", default="50%", type="string",
    "-W", "--buffer-warning", default="50%", type="string",
    help="Warning threshold buffer_total_queued_size (default: buffer_total_queued_size * 50%)",
    dest="b_warn")
parser.add_option(
    # "-C", "--buffer-critical", default="80%", type="string",
    "-C", "--buffer-critical", default="80%", type="string",
    help="Critical threshold buffer_total_queued_size (default: buffer_total_queued_size * 80%)",
    dest="b_crit")
parser.add_option(
    "-p", "--print", action="store_true", dest="printflg",
    help="Print parsed Fluentd metrics")
(options, args) = parser.parse_args()


def get_metrics():
    url = "http://" + options.url + "/api/plugins.json"
    request = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(request)
    results = json.loads(f.read())
    return results['plugins']


def print_metrics():
    results = get_metrics()
    for result in results:
        print json.dumps(result, indent=4, sort_keys=True)
    sys.exit(STATUS_OK)


def cast_opts(threshold):
    threshold = float(re.search(r'[0-9]+', threshold).group(0)) / 100
    return threshold


def check_count(count, warning, critical, result):
    if count is not None:
        if count >= critical:
            print "CRITICAL: retry_count is %d, crit:%d, config:%s" \
                % (count, critical, result['config'])
            sys.exit(STATUS_CRITICAL)
        if count >= warning:
            print "WARNING: retry_count is %d, warn:%d, config:%s" \
                % (count, warning, result['config'])
            sys.exit(STATUS_WARNING)


def check_buff_size(b_size, b_warning, b_critical, result):
    if b_size is not None:
        if b_size >= b_critical:
            print "CRITICAL: buffer_total_queued_size is %d, crit:%d" \
                % (b_size, b_critical)
            sys.exit(STATUS_CRITICAL)
        if b_size >= b_warning:
            print "WARNING: buffer_total_queued_size is %d, warn:%d" \
                % (b_size, b_warning)
            sys.exit(STATUS_WARNING)


def set_count_threshold(result, threshold):
    if 'retry_limit' in result['config']:
        threshold = int(result['config']['retry_limit']) - threshold
    else:
        threshold = DEFAULT_LIMIT - threshold
    return threshold


def set_buff_size_threshold(result, threshold):
    if 'buffer_chunk_limit' in result['config']:
        chunk_limit = int(result['config']['buffer_chunk_limit'])
    else:
        chunk_limit = DEFAULT_CHUNK_LIMIT
    if 'buffer_queue_limit' in result['config']:
        queue_limit = int(result['config']['buffer_queue_limit'])
    else:
        queue_limit = DEFAULT_QUEUE_LIMIT
    threshold = chunk_limit * queue_limit * threshold
    return threshold


def varidate_metrics(results):
    for result in results:
        if result['retry_count'] is not None:
            return None
    print "UNKNOWN: retry_count metric does not exist."
    sys.exit(STATUS_UNKNOWN)


def main():
    results = get_metrics()
    if options.printflg:
        print_metrics()
    varidate_metrics(results)
    for result in results:
        warn = set_count_threshold(result, options.warn)
        crit = set_count_threshold(result, options.crit)
        b_warn = set_buff_size_threshold(result, cast_opts(options.b_warn))
        b_crit = set_buff_size_threshold(result, cast_opts(options.b_crit))
        check_count(result['retry_count'], warn, crit, result)
        if 'buffer_total_queued_size' in result:
            check_buff_size(result['buffer_total_queued_size'], b_warn, b_crit, result)
    print "OK: All retry_count and buffer_total_queued_size is OK"
    sys.exit(STATUS_OK)

if __name__ == '__main__':
    main()
