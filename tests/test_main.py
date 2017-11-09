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
    res = main._random()
    assert res == json.dumps({'result': v})


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


@mock.patch('mytest.main.app.config',
            return_value={'UPSTREAM_TIMEOUT': 123})
@mock.patch('mytest.main.make_response', side_effect=lambda x: x[0])
@mock.patch('mytest.main.requests.Session')
@mock.patch('mytest.main.json.jsonify', side_effect=_jsonmock)
@mock.patch('mytest.main.MyFlask.wikistats_increment')
@pytest.mark.parametrize('get,exc,expected', [
    (
        [
            {'query': {'pages': {'qwe': {'pageid': 123}}}},
            {'parse': {'parsetree': {'qwe': '<root>qwe</root>'}}},
            None,
        ],
        None,
        json.dumps({"result": "<root>qwe</root>"})
    ),
    (
        [
            {'query': {'pages': {'asd': {'pageid': 234}}}},
            {'parse': {'parsetree': {'asd': '<root>#REDIRECT [[asd]]</root>'}}},
            {'parse': {'parsetree': {'asd': '<root>asd</root>'}}},
        ],
        None,
        json.dumps({"result": "<root>asd</root>"})
    ),
    (
        [
            {'query': {'pages': {'asd': {'error': 'asd'}}}},
            None,
            None,
        ],
        None,
        json.dumps({"message": "No such wiki: qwe"})
    ),
    (
        [
            {'query': {'pages': {'asd': {'pageid': 234}}}},
            {'error': 'qweqwe'},
            None,
        ],
        Exception,
        None
    ),

])
def test__wikipedia(wikistats_increment,
                    jsonify,
                    Session,
                    make_response,
                    config,
                    get,
                    exc,
                    expected):
    Session.return_value.get.return_value.json.side_effect = get
    if exc:
        res = None
        with pytest.raises(exc):
            main._wikipedia('qwe')
    else:
        res = main._wikipedia('qwe')
    assert res == expected


@mock.patch('mytest.main.json.jsonify', side_effect=_jsonmock)
@mock.patch('mytest.main.app.wikistats_items')
@mock.patch('mytest.main.request')
@pytest.mark.parametrize('v,n,exp', [
    (
        [('qwe', 1), ('asd', 2), ('zxc', 3)],
        3,
        json.dumps({'result': ['zxc', 'asd', 'qwe']})
    ),
])
def test__stats_get(request, wikistats_items, jsonify, v, n, exp):
    request.authorization = {'username': 'qwe'}
    wikistats_items.return_value = v
    res = main._stats_get(n)
    assert res == exp


@mock.patch('mytest.main.make_response', side_effect=lambda x: x[0])
@mock.patch('mytest.main.json.jsonify', side_effect=_jsonmock)
@mock.patch('mytest.main.request')
@pytest.mark.parametrize('auth, exp', [
    ({'username': 'qwe'}, {"result": "ok"}),
    (None, {"message": "Authentication required (fake)"} )
])
def test__stats_reset(request, jsonify, make_response, auth, exp):
    request.authorization = auth
    res = main._stats_reset()
    assert res == json.dumps(exp)


@mock.patch('mytest.main.requests.Session')
@mock.patch('mytest.main.json.jsonify', side_effect=_jsonmock)
@pytest.mark.parametrize('v', [
    (
        { 'type': 'success', 'value': { 'joke': 'qweqwe' } },
        None,
        json.dumps({'result': 'qweqwe'}),
    ),
    (
        { 'type': 'error', 'value': { 'joke': 'qweqwe' } },
        Exception,
        None
    ),

])
def test__joke(jsonify, Session, v):
    Session.return_value.get.return_value.json.return_value = v[0]
    if v[1]:
        res = None
        with pytest.raises(v[1]):
            main._joke()
    else:
        res = main._joke()
    assert res == v[2]
