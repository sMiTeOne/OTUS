import hashlib
import datetime
import unittest
import functools
import unittest.mock

import api
import pytest
import scoring
from enums import HTTPStatus
from store import Store


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for case in cases:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                f(*new_args)

        return wrapper

    return decorator


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.settings = {}

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.settings)

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            raw_string = datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT
        else:
            raw_string = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(raw_string.encode('utf-8')).hexdigest()

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(HTTPStatus.INVALID_REQUEST, code)

    @cases(
        [
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
            {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
        ]
    )
    def test_bad_auth(self, request):
        _, code = self.get_response(request)
        self.assertEqual(HTTPStatus.FORBIDDEN, code)

    @cases(
        [
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
            {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
            {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
        ]
    )
    def test_invalid_method_request(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(HTTPStatus.INVALID_REQUEST, code)
        self.assertTrue(len(response))

    @cases(
        [
            {},
            {"phone": "79175002040"},
            {"phone": "89175002040", "email": "stupnikov@otus.ru"},
            {"phone": "79175002040", "email": "stupnikovotus.ru"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": 1,
            },
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": "s",
                "last_name": 2,
            },
            {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
            {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
        ]
    )
    def test_invalid_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(HTTPStatus.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases(
        [
            {"phone": "79175002040", "email": "stupnikov@otus.ru"},
            {"phone": 79175002040, "email": "stupnikov@otus.ru"},
            {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
            {"gender": 0, "birthday": "01.01.2000"},
            {"gender": 2, "birthday": "01.01.2000"},
            {"first_name": "a", "last_name": "b"},
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": "a",
                "last_name": "b",
            },
        ]
    )
    def test_ok_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        with unittest.mock.patch('store.Store.__init__'):
            response, code = self.get_response(request)
        self.assertEqual(HTTPStatus.OK, code, arguments)
        score = response.get("score")
        self.assertTrue(isinstance(score, (int, float)) and score >= 0, arguments)
        self.assertEqual(sorted(self.context["has"]), sorted(arguments.keys()))

    def test_ok_score_admin_request(self):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(HTTPStatus.OK, code)
        score = response.get("score")
        self.assertEqual(score, 42)

    @cases(
        [
            {},
            {"date": "20.07.2017"},
            {"client_ids": [], "date": "20.07.2017"},
            {"client_ids": {1: 2}, "date": "20.07.2017"},
            {"client_ids": ["1", "2"], "date": "20.07.2017"},
            {"client_ids": [1, 2], "date": "XXX"},
        ]
    )
    def test_invalid_interests_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(HTTPStatus.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases(
        [
            {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
            {"client_ids": [1, 2], "date": "19.07.2017"},
            {"client_ids": [0]},
        ]
    )
    def test_ok_interests_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.set_valid_auth(request)
        with unittest.mock.patch('store.Store.get') as mock:
            mock.return_value = None
            response, code = self.get_response(request)
        self.assertEqual(HTTPStatus.OK, code, arguments)
        self.assertEqual(len(arguments["client_ids"]), len(response))
        self.assertTrue(
            all(isinstance(v, list) and all(isinstance(i, (bytes, str)) for i in v) for v in response.values())
        )
        self.assertEqual(self.context.get("nclients"), len(arguments["client_ids"]))


@pytest.mark.parametrize(
    'arguments, cache_value, expected_value',
    (
        (
            {"phone": "79175002040", "email": "stupnikov@otus.ru"},
            None,
            3.0,
        ),
        (
            {"phone": "79175002040", "email": "stupnikov@otus.ru"},
            [['uid:3f76818f507fe7eb6422bd0703c64c88', 3.0]],
            3.0,
        ),
    ),
)
def test_get_score(mocker, arguments, cache_value, expected_value):
    users_store = Store('users')
    mocker.patch.object(Store, 'cache_get', return_value=cache_value)
    with unittest.mock.patch('store.Store.cache_set') as cache_set:
        actual_value = scoring.get_score(users_store, **arguments)
        assert cache_set.called is not bool(cache_value)

    assert actual_value == expected_value


@pytest.mark.parametrize(
    'client_id, cache_value, expected_value',
    (
        (
            1,
            None,
            [],
        ),
        (
            1,
            [['cid:1', ['cars', 'sport']]],
            ['cars', 'sport'],
        ),
    ),
)
def test_get_interests(mocker, client_id, cache_value, expected_value):
    mocker.patch.object(Store, 'get', return_value=cache_value)
    clients_store = Store('clients')
    actual_value = scoring.get_interests(clients_store, client_id)

    assert actual_value == expected_value


if __name__ == "__main__":
    unittest.main()
