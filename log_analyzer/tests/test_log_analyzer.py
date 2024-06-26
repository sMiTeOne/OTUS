import os
import unittest

from log_analyzer import (
    LogFile,
    get_analyzed_log,
)


class LogAnalyzerTest(unittest.TestCase):
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    def test_wrong_log_files(self):
        self.assertIsNone(get_analyzed_log(f'{self.DIR_PATH}/log_dirs/wrong_log_files'))

    def test_analyzed_log_exist(self):
        actual = get_analyzed_log(f'{self.DIR_PATH}/log_dirs/analyzed_log_exist')
        expected = LogFile('log-20220630.gz', '20220630', 'gz')
        self.assertEqual(actual, expected)

    def test_several_log_files(self):
        actual = get_analyzed_log(f'{self.DIR_PATH}/log_dirs/several_log_files')
        expected = LogFile('log-20220630.gz', '20220630', 'gz')
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
