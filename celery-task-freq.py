#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import datetime


if len(sys.argv) < 3:
    print('Usage: celery-task-fred.py <log_path> <task_name>')
    sys.exit(1)

LOG_PATH = sys.argv[1]
FILTER_TASK = sys.argv[2]


def get_time(line):
    """
    Return a datetime object from a string

    >>> get_time('[2012-10-17 01:56:53,802: INFO/MainProcess] Task')
    datetime.datetime(2012, 10, 17, 1, 56, 53)
    """
    time_mark = re.search('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
    if time_mark:
        date_str = time_mark.group(1)
        date_format = '%Y-%m-%d %H:%M:%S'
        return datetime.datetime.strptime(date_str, date_format)


def get_duration(line):
    """
    Return seconds for a task log line.

    >>> get_duration('succeeded in 11.3482778072s: None')
    11

    """
    duration = re.search(' in (\d+)\.\d+s', line)
    if duration:
        return int(duration.group(1))


def collect_data(lines):
    """
    Return a list of tuples (time, duration) from a list of lines.
    >>> lines = [
    ... '[2012-10-16 16:34:08,087: INFO/MainProcess] Task\
    ...  update_annonce_profile[876c015f] succeeded in 11.5902109146s: None',
    ... '[2012-10-16 17:14:03,027: INFO/MainProcess] Task\
    ...  update_annonce_profile[4ede4354] succeeded in 5.1678210128s: None',
    ... ]
    >>> collect_data(lines)
    [(datetime.datetime(2012, 10, 16, 16, 34, 8), 11), (datetime.datetime(2012, 10, 16, 17, 14, 3), 5)]

    """
    data = []
    for line in lines:
        time = get_time(line)
        duration = get_duration(line)
        data.append((time, duration))
    return data


def stats_by_hour(data):
    """
    Print the ocurrence number by hour.

    >>> data = [
    ... (datetime.datetime(2012, 10, 16, 16, 34, 8), 11),
    ... (datetime.datetime(2012, 10, 16, 16, 47, 2), 11),
    ... (datetime.datetime(2012, 10, 16, 17, 14, 3), 5),
    ... ]
    >>> stats_by_hour(data)
    Date: 10/16/12
    16: ## 2
    17: # 1
    """
    hour = None
    count = 0
    for time, duration in data:
        if hour is None:
            sys.stdout.write('Date: %s\n' % time.strftime('%x'))
        if hour != time.hour:
            if not hour is None:
                sys.stdout.write(' %d\n' % count)
                count = 0
            hour = time.hour
            sys.stdout.write('%.2d: #' % hour)
            count += 1
        else:
            count += 1
            sys.stdout.write('#')
    sys.stdout.write(' %d\n' % count)


def main():
    filtered_lines = []
    with open(LOG_PATH) as log_file:
        for line in log_file.readlines():
            if FILTER_TASK in line:
                filtered_lines.append(line.strip())
    data = collect_data(filtered_lines)
    stats_by_hour(data)


if __name__ == '__main__':
    main()
