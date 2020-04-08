import json
import time
from datetime import datetime, timedelta
from pprint import pprint
from random import randint
from urllib.parse import urljoin

import requests

from core.cls import Recommendation, Match, Person, Profile, Message


class TinderAPI:
    headers = {}
    x_auth_token = None
    base_url = "https://api.gotinder.com"

    POST = 'POST'
    GET = 'GET'

    def __init__(self, x_auth_token):
        self.x_auth_token = x_auth_token
        self.init_headers()
        self.match_person_ids = [m.person.person_id for m in self.matches]
        self.profile = self.get_profile()

    def init_headers(self):
        self.headers['User-agent'] = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"
        self.headers['Content-type'] = "application/json"
        if not self.x_auth_token:
            raise AttributeError('x_auth_token is not set')

        self.headers['X-Auth-Token'] = self.x_auth_token

    def request(self, url, method=GET, data=None, params=None, *args, **kwargs):
        _url = urljoin(self.base_url, url)
        if method is self.GET:
            r = requests.get(url=_url, params=params or None, headers=self.headers, **kwargs)
        elif method is self.POST:
            r = requests.post(url=_url, data=data or None, headers=self.headers, *args, **kwargs)
        else:
            raise AttributeError('Please check method parameter')

        if r.status_code != 200:
            pprint(r.__dict__)
            raise Exception("Error while requesting '%s'\n (%s)" % (_url, r.content))

        return r

    def get_user_recs(self):
        """

        :return: Returns recommendations
        :rtype: list of Recommendation
        """
        r = self.request('/user/recs')
        recs = []
        for rec in r.json().get('results', []):
            recs.append(Recommendation(**{
                'bio': rec.get('bio'),
                'name': rec.get('name'),
                'user_id': rec.get('_id'),
            }))
        return recs

    def get_profile(self):
        r = self.request('/profile')
        if not r.status_code == 200:
            return
        return Profile(
            user_id=r.json().get('_id')
        )

    def like(self, user_id):
        r = self.request('/like/{user_id}'.format(user_id=user_id))
        data = r.json()
        if data.get('likes_remaining', 0) < 1:
            date = datetime.fromtimestamp(data.get('rate_limited_until') / 1000)
            print("No more likes -- have to wait until %s" % date)
            _delta = date - datetime.now()
            time.sleep(_delta.seconds)
            return False
        return {
            'likes_remaining': data.get('likes_remaining'),
            'match': data.get('match'),
        } if r.status_code == 200 else False

    def dislike(self, user_id):
        r = self.request('/pass/{user_id}'.format(user_id=user_id))
        return r if r.status_code == 200 else False

    @property
    def matches(self):
        params = {
            'messages': 0,
            'count': 60,
            'is_tinder_u': 'false',
            'locale': 'de'
        }
        r = self.request('/v2/matches', params=params)
        data = r.json().get('data', None)

        matches = []
        for match in data.get('matches'):
            msgs = []
            for msg in match.get('messages', []):
                m = Message(**msg)
                msgs.append(m)
            p = Person()
            p.person_id = match['person']['_id']
            p.name = match['person']['name']

            m = Match(**{
                'message_count': match['message_count'],
                'match_id': match['id'],
                'person': p,
                'messages': msgs
            })
            matches.append(m)

        print("Found %i matches" % (len(data.get('matches'))))
        return matches

    def message(self, match_id, message):
        return self.request('/user/matches/{user_id}'.format(user_id=match_id),
                            method=TinderAPI.POST, json={"message": message})


class TinderBot:
    def __init__(self, x_auth_token, is_message_on_match=False):
        self.api = TinderAPI(x_auth_token)
        self.is_message_on_match = is_message_on_match
        self.starter_lines = TinderBot.get_starters_from_file("messages.txt")

    @staticmethod
    def sleep(seconds, show_print=True):
        if show_print:
            print("Waiting %s seconds" % seconds)
        time.sleep(seconds)

    def random_like(self,):
        size_prop = 10
        dislike_on = [2, 4]     # numbers from , if match -> dislike (like 80%)

        while True:
            print("Getting Recs")
            recs = self.api.get_user_recs()
            if len(recs) < 1:
                print("-- no more Recs --")
                self.sleep(120)
                continue

            for rec in recs:
                if randint(0, size_prop) in dislike_on:
                    if self.api.dislike(rec.user_id):
                        print("Passed on '{name}'".format(name=rec.name))
                else:
                    r = self.api.like(rec.user_id)
                    if not r:
                        continue

                    print("Liked '{name}'".format(name=rec.name))
                    if r.get('match', False):
                        print("!!! Matched '%s'" % (rec.name,))
                        self.message_starter()

                self.sleep(randint(1, 3), show_print=False)
            self.sleep(randint(10, 60))

    def message_starter(self):
        for match in self.api.matches:
            if len(match.messages) < 1:
                self.message_match(match)
                self.sleep(randint(1, 3))

    def message_match(self, match):
        line = self.starter_lines[randint(0, len(self.starter_lines)-1)]
        r = self.api.message(match.match_id, line.format(name=match.person.name))
        print("Sending '%s' the message '%s...'" % (match.person.name, line[:10]))
        if not r.status_code:
            print("Error sending message")
            print(r.content)
        return r

    @staticmethod
    def get_starters_from_file(path):
        with open(path, 'r') as f:
            lines = f.read().splitlines()
        return lines


