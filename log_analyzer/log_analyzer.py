#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import json
import typing
import logging
import argparse

parser = argparse.ArgumentParser(description='Log analyzer')
parser.add_argument('--config', help='Config file path', default='config.json')
parsed_args = parser.parse_args()

logger = logging.getLogger(__name__)

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def get_config() -> dict[str, typing.Any]:
    with open(parsed_args.config, 'r') as f:
        json_config = json.load(f)
        config.update(json_config)
    return config


def set_logging_settings(config: dict[str, typing.Any]) -> None:
    logging.basicConfig(
        filename=config.get('LOG_FILE_NAME'),
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
        level=logging.DEBUG,
    )


def main():
    config = get_config()
    set_logging_settings(config=config)


if __name__ == "__main__":
    main()
