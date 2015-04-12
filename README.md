# check_fluentd

This is a plugin for Nagios that will check Fluentd internal metrics (from monitor_agent plugin)

# Usage

  Usage: check_fluentd.py [options]
  
  Options:
    -h, --help            show this help message and exit
    -u URL, --url=URL     Fluentd monitor_agent URL (default: localhost:24220)
    -w WARN, --warning=WARN
                          warning threthold (default: retry_limit - 5)
    -c CRIT, --critical=CRIT
                          critical threthold (default: retry_limit - 3)
    -p, --print           Print parsed Fluentd metrics

