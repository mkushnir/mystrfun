#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import logging
import logging.handlers
import os
import requests
import shelve
import sys
import urllib
import signal

from flask import Flask, json, make_response


def _myterm(signum, frame):
    app.wikistats_close()
    sys.exit(0)


signal.signal(signal.SIGINT, _myterm)
signal.signal(signal.SIGTERM, _myterm)


# Configuration
_default_config = {
    'DEBUG': True,
    'TESTING': False,
    'LOGGER_HANDLER_POLICY': 'always',
    'LOG_FILE': None,
    'LOG_LEVEL': 'INFO',
    'LOG_BACKUP_COUNT': 10,
    'LOG_MAX_BYTES': 1024*1024,
    'LOG_ONELINE': True,

    'UPSTREAM_TIMEOUT': 15,
    'WIKISTATS_FILE': None, #'wikistats.db',
}


_log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}


class MyFlask(Flask):
    def __init__(self, *args, **kwargs):
        # guard one time configuring
        self._configured = False

        # a persistent disctionary to store wiki stats
        self._wikistats = None

        super(MyFlask, self).__init__(*args, **kwargs)

    def wikistats_increment(self, word):
        """
        Increment wiki stats for the given word

        :param word: the key to increment stats
        """
        if word in self._wikistats:
            v = self._wikistats[word] + 1
        else:
            v = 1
        self._wikistats[word] = v
        # self._wikistats.sync()

    def wikistats_items(self):
        return self._wikistats.iteritems()

    def _wikistats_open(self):
        if self.config['WIKISTATS_FILE']:
            self._wikistats = shelve.open(
                self.config['WIKISTATS_FILE'], writeback=True)
        else:
            self._wikistats = collections.defaultdict(int)

    def wikistats_close(self):
        # take care
        if self._wikistats:
            try:
                self._wikistats.close()
            except AttributeError:
                # in case it's defaultdict, has no such method
                self.logger.warning('An attempt to close() a non-persistent '
                                    'database.  Ignoring.')

            self._wikistats = None

    def wikistats_clear(self):
        if self._wikistats:
            self._wikistats.clear()

    def configure(self, configfile):
        if self._configured:
            return

        # default config
        self.config.from_mapping(_default_config)

        if configfile:
            # override from file
            self.config.from_json(configfile)

        if self.config['LOG_FILE']:
            file_handler = logging.handlers.RotatingFileHandler(
                self.config['LOG_FILE'],
                backupCount=self.config['LOG_BACKUP_COUNT'],
                maxBytes=self.config['LOG_MAX_BYTES'])
        else:
            file_handler = logging.StreamHandler(sys.stderr)

        file_handler.setLevel(
            _log_levels.get(self.config['LOG_LEVEL'], logging.NOTSET))
        if self.config['LOG_ONELINE']:
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        else:
            file_handler.setFormatter(logging.Formatter('''
Message type: %(levelname)s
Location:     %(pathname)s:%(lineno)d
Time:         %(asctime)s

%(message)s
        '''))
        self.logger.addHandler(file_handler)

        # this must always start clear
        assert self._wikistats is None
        self._wikistats_open()
        self._configured = True


app = MyFlask(__name__)


@app.before_first_request
def _before_first_request():
    # one time action
    app.configure(os.environ.get('MYTEST_CONFIGFILE'))


@app.errorhandler(Exception)
def eh(error):
    app.logger.exception('Unhandled exception: %s', error)
    if app.config['DEBUG']:
        return json.jsonify(error_message=str(error)), 500
    else:
        return json.jsonify(
            error_message='Application Error. Please contact support '
            'at support@mytest.com'), 500


@app.route('/')
def index():
    return json.jsonify(result='ok')


@app.route('/random')
def _random():
    response = requests.get('http://setgetgo.com/randomword/get.php',
                            timeout=app.config['UPSTREAM_TIMEOUT'])
    return json.jsonify(result=response.content)


def _normalize_word(word):
    if isinstance(word, unicode):
        word = word.encode('utf-8')
    word = word.lower()
    word = urllib.quote(word)
    return word


def _get_wiki(session, pageid, redirects=False):
    if redirects:
        redir = '&redirects'
    else:
        redir = ''

    response = session.get('https://en.wikipedia.org/w/api.php?'
                           'format=json&'
                           'action=parse&'
                           'pageid=%d&'
                           'prop=parsetree%s' % (pageid, redir),
                           timeout=app.config['UPSTREAM_TIMEOUT'])
    result = response.json()
    if 'error' in result:
        raise Exception('Could not parse. Error: %r' % result)

    v = result['parse']['parsetree'].values()[0]
    return v


@app.route('/wikipedia/<word>')
def _wikipedia(word):
    session = requests.Session()

    w = _normalize_word(word)
    app.wikistats_increment(w)

    response = session.get('https://en.wikipedia.org/w/api.php?'
                           'format=json&action=query&titles=%s' % w,
                           timeout=app.config['UPSTREAM_TIMEOUT'])
    result = response.json()
    v = result['query']['pages'].values()[0]

    if 'pageid' not in v:
        return make_response(
            (json.jsonify(message='No such wiki: %s' % w), 404, []))

    w = _get_wiki(session, v['pageid'], False)
    if '#REDIRECT' in w:
        w = _get_wiki(session, v['pageid'], True)

    return json.jsonify(result=w)


@app.route('/stats/<int:n>')
def _stats_get(n):
    r = sorted(((v, k) for k, v in app.wikistats_items()), reverse=True)[:n]
    return json.jsonify(result=[i[1] for i in r])


@app.route('/stats/reset', methods=['POST'])
def _stats_reset():
    app.wikistats_clear()
    return json.jsonify(result='ok')


@app.route('/joke/<first>/<last>')
@app.route('/joke/<first>')
@app.route('/joke')
def _joke(first='Chuck', last='Norris'):
    session = requests.Session()

    first = _normalize_word(first)
    last = _normalize_word(last)
    response = session.get(
        'http://api.icndb.com/jokes/random?firstName=%s&lastName=%s' %
        (first, last))

    v = response.json()
    if v['type'] != 'success':
        raise Exception('Could not make a joke: response headers %r body %r' %
                        (response.headers, response.content))

    return json.jsonify(result=v['value']['joke'])
