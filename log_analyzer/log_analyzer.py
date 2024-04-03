#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import os
import re
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
    with open(parsed_args.config, 'r') as f:
        json_config = json.load(f)
        config.update(json_config)
    return config


def set_logging_config(config: dict[str, typing.Any]) -> None:
    logging.basicConfig(
        filename=config.get('LOG_FILE_NAME'),
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
        level=logging.DEBUG,
    )


def get_last_log_file(config: dict[str, typing.Any]) -> LogFile | None:
    last_log_file = None
    try:
        for file_name in os.listdir(config.get('LOG_DIR')):
            matched_groups = re.findall(r'(.*([\d]{8}).*\.(\w+))', file_name)
            if matched_groups:
                current_log_file = LogFile(*matched_groups[0])
                if last_log_file is None or last_log_file.date < current_log_file.date:
                    last_log_file = current_log_file
    except FileNotFoundError:
        logger.exception('Logging dir is not found')
    return last_log_file


def main():
    config = get_config()
    set_logging_config(config=config)
    last_log_file = get_last_log_file(config=config)


if __name__ == "__main__":
    main()
