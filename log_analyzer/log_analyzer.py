#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import gzip
import json
import logging
import argparse
from statistics import median
from collections import namedtuple

parser = argparse.ArgumentParser(description='Log analyzer')
parser.add_argument('--config', help='Config file path', default='config.json')

logger = logging.getLogger(__name__)

LogFile = namedtuple('LogFile', 'name, date, extension')
Counters = namedtuple('Counters', 'items, time, errors')

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}

LOG_FILE_REGEX = re.compile(r'^(.*([\d]{8}).*\.(log|txt|gz))$')
REQUEST_URL_REGEX = re.compile(r'^\/.+$')
RESPONSE_TIME_REGEX = re.compile(r'^\d+\.\d{3}$')


def initialize_dirs(dirs: tuple[str, str]) -> None:
    try:
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)
    except Exception as error:
        logger.exception('Failed to create directory %s. Error: %s', dir, error)


def get_config(config: dict) -> dict:
    try:
        config_file_path = parser.parse_args().config
        with open(config_file_path) as f:
            json_config = json.load(f)
            config.update(json_config)
    except FileNotFoundError as error:
        logger.exception('Config file %s was not found. Error %s', config_file_path, error)
    return config


def set_logging_config(filename: str) -> None:
    try:
        logging.basicConfig(
            filename=filename,
            level=logging.DEBUG,
            datefmt='%Y.%m.%d %H:%M:%S',
            format='[%(asctime)s] %(levelname).1s %(message)s',
        )
    except FileNotFoundError as error:
        logger.exception('Unable to create log file %s. Error %s', filename, error)


def create_report(analyzed_data: list[dict], report_filepath: str) -> None:
    try:
        with open('report.html', 'r') as template_file, open(report_filepath, 'a') as report_file:
            template = template_file.read()
            rendered_template = template.replace('$table_json', str(analyzed_data))
            report_file.write(rendered_template)
    except FileNotFoundError as error:
        logger.exception('Template file missing. Error %s', error)


def get_analyzed_log(log_dir: str) -> LogFile | None:
    last_log_file = None
    for file_name in os.listdir(log_dir):
        if matched_groups := LOG_FILE_REGEX.findall(file_name):
            current_log_file = LogFile(*matched_groups[0])
            if last_log_file is None or last_log_file.date < current_log_file.date:
                last_log_file = current_log_file
    return last_log_file


def get_raw_log_analysis(log_dir: str, log_file: LogFile) -> tuple[dict, Counters]:
    counters = Counters(0, 0, 0)
    analyzed_data = {}
    initial_dict = {
        'count': 0,
        'time_avg': 0,
        'time_max': 0,
        'time_sum': 0,
        'values': [],
    }

    file_open_func = gzip.open if log_file.extension == 'gz' else open

    with file_open_func(os.path.join(log_dir, log_file.name), mode='rt') as file:
        for line in file:
            splitted_line = line.split()
            request_url = splitted_line[6]
            response_time = splitted_line[-1]

            if not REQUEST_URL_REGEX.match(request_url) or not RESPONSE_TIME_REGEX.match(response_time):
                logger.debug('Wrong request url or request time format')
                counters = Counters(counters.items + 1, counters.time, counters.errors + 1)
                continue

            response_time = float(response_time)
            counters = Counters(counters.items + 1, counters.time + response_time, counters.errors)

            url_stats = analyzed_data.setdefault(request_url, initial_dict.copy())
            url_stats['count'] += 1
            url_stats['values'].append(response_time)
            url_stats['time_max'] = max(url_stats['time_max'], response_time)
            url_stats['time_sum'] = round(url_stats['time_sum'] + response_time, 3)
            url_stats['time_avg'] = round(
                ((url_stats['count'] - 1) * url_stats['time_avg'] + response_time) / url_stats['count'], 3
            )

    return analyzed_data, counters


def get_clear_analyzed_data(raw_analyzed_data: dict, item_counter: int, time_counter: float):
    for url, stats in sorted(raw_analyzed_data.items(), key=lambda kv: kv[1]['time_sum'], reverse=True):
        logger.debug('Collecting statistic for url %s', url)
        yield {
            'url': url,
            'count': stats['count'],
            'time_max': stats['time_max'],
            'time_sum': stats['time_sum'],
            'time_avg': stats['time_avg'],
            'time_med': median(stats['values']),
            'time_perc': round(stats['time_sum'] / time_counter, 3),
            'count_perc': round(stats['count'] / item_counter, 3),
        }


def main(config: dict) -> None:
    try:
        config = get_config(config)

        log_dir = config.get('LOG_DIR')
        report_dir = config.get('REPORT_DIR')
        report_size = config.get('REPORT_SIZE')
        log_filename = config.get('LOG_FILENAME')
        error_threshold = config.get('ERROR_THRESHOLD')

        set_logging_config(log_filename)
        initialize_dirs((log_dir, report_dir))

        if log_file := get_analyzed_log(log_dir):
            report_filepath = os.path.join(report_dir, f'report-{log_file.date}.html')
            if not os.path.exists(report_filepath):
                raw_analyzed_data, counters = get_raw_log_analysis(log_dir, log_file)
                if not error_threshold or error_threshold > counters.errors / counters.items:
                    data_generator = get_clear_analyzed_data(raw_analyzed_data, counters.items, counters.time)
                    real_report_size = min(report_size, counters.items)
                    analyzed_data = [next(data_generator) for _ in range(real_report_size)]
                    create_report(analyzed_data, report_filepath)
                else:
                    logger.info('Failed to parse log file')
            else:
                logger.info('Log file has already been analyzed')
        else:
            logger.info('No log files for analysis')
    except Exception as error:
        logger.exception('Unexpected error: %s', error)


if __name__ == "__main__":
    main(config=config)
