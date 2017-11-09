# -*- coding: utf-8 -*-
import os
import sys
import json

import pytest
import mock

def _package_root():
    # move ../.. from here
    return os.path.dirname(os.path.dirname(__file__))

sys.path.append(os.path.join(_package_root(), 'src'))

import mytest.main as main


def _jsonmock(**kwargs):
    return json.dumps(kwargs)


@mock.patch('mytest.main.app.config',
            return_value={'UPSTREAM_TIMEOUT': 123})
@mock.patch('mytest.main.requests.get')
@mock.patch('mytest.main.json.jsonify', side_effect=_jsonmock)
@pytest.mark.parametrize('v', [
        'qwe',
        'asd',

])
def test__random(jsonify, get, config, v):
    get.return_value.content = v
    main._random()


@pytest.mark.parametrize('v', [
    ('asd', 'asd', None),
    ('asd qwe', 'asd%20qwe', None),
    (u'asd qwe', 'asd%20qwe', None),
    (u'привіт', '%D0%BF%D1%80%D0%B8%D0%B2%D1%96%D1%82', None),
])
def test__normalize_word(v):
    if v[2] is None:
        assert main._normalize_word(v[0]) == v[1]
    else:
        with pytest.raises(v[2]):
            main._normalize_word(v[0]) == v[1]


@mock.patch('mytest.main.requests.Session')
@mock.patch('mytest.main.json.jsonify', side_effect=_jsonmock)
@pytest.mark.parametrize('v', [
    (
        { 'type': 'success', 'value': { 'joke': 'qweqwe' } },
        None,
    ),
    (
        { 'type': 'error', 'value': { 'joke': 'qweqwe' } },
        Exception,
    ),

])
def test__joke(jsonify, Session, v):
    Session.return_value.get.return_value.json.return_value = v[0]
    if v[1]:
        with pytest.raises(v[1]):
            main._joke()
    else:
        main._joke()
