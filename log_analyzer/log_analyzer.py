#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import os
import re
import gzip
import json
import typing
import logging
import argparse
from collections import namedtuple

parser = argparse.ArgumentParser(description='Log analyzer')
parser.add_argument('--config', help='Config file path', default='config.json')
parsed_args = parser.parse_args()

logger = logging.getLogger(__name__)

LogFile = namedtuple('LogFile', 'name, date, extension')

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}


def get_config() -> dict[str, typing.Any]:
    with open(parsed_args.config) as f:
        json_config = json.load(f)
        config.update(json_config)
    return config


def set_logging_config(filename: str) -> None:
    logging.basicConfig(
        filename=filename,
        level=logging.DEBUG,
        datefmt='%Y.%m.%d %H:%M:%S',
        format='[%(asctime)s] %(levelname).1s %(message)s',
    )


def get_last_log_file(log_dir: str) -> LogFile | None:
    last_log_file = None
    try:
        for file_name in os.listdir(log_dir):
            matched_groups = re.findall(r'(.*([\d]{8}).*\.(log|txt|gz))', file_name)
            if matched_groups:
                current_log_file = LogFile(*matched_groups[0])
                if last_log_file is None or last_log_file.date < current_log_file.date:
                    last_log_file = current_log_file
    except FileNotFoundError:
        logger.exception('Logging dir is not found')
    return last_log_file


def analyse_log(log_dir: str, log_file: LogFile | None):
    analyzed_data = {}
    initial_dict = dict.fromkeys(('count', 'time_avg', 'time_max', 'time_sum', 'time_med', 'time_perc', 'count_perc'), 0)

    if log_file is None:
        logger.info('There is no required file for log analysis')
    
    file_open_func = gzip.open if log_file.extension == 'gz' else open

    with file_open_func(os.path.join(log_dir, log_file.name), mode='rt') as file:
        for line in file:
            splitted_line = line.split()
            request_url = splitted_line[6]
            response_time = float(splitted_line[-1])

            url_stat = analyzed_data.setdefault(request_url, initial_dict.copy())
            url_stat['count'] += 1
            url_stat['time_sum'] += response_time
            url_stat['time_max'] = max(url_stat['time_max'], response_time)

    return analyzed_data

def main():
    config = get_config()

    log_dir = config.get('LOG_DIR')
    log_filename = config.get('LOG_FILENAME')

    set_logging_config(log_filename)
    log_file = get_last_log_file(log_dir)
    analyzed_data = analyse_log(log_dir, log_file)


if __name__ == "__main__":
    main()
