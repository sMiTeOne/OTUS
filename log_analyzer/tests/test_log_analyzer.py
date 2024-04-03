import unittest

from log_analyzer import (
    LogFile,
    get_analyzed_log,
)


class LogAnalyzerTest(unittest.TestCase):
    def test_empty_log_dir(self):
        self.assertIsNone(get_analyzed_log('./log_dirs/empty_log_dir'))

    def test_analyzed_log_exist(self):
        actual = get_analyzed_log('./log_dirs/analyzed_log_exist')
        expected = LogFile('log-20220630.gz', '20220630', 'gz')
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
