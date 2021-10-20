import json
from threading import Thread
from typing import Optional

from flask import Flask, jsonify, request, Response
from requests import post

from .classes import CogPlus, BotPlus
from .extra import __agent__
from .task import TaskPlus


class API(CogPlus):
    def __init__(self, bot: BotPlus, import_name, **kwargs):
        self.bot = bot
        self.app = Flask(import_name, **kwargs)
        self._auth = None
        self._thread = None

        self.app.add_url_rule('/', None, self.ping)
        self.app.add_url_rule('/ping', None, self.ping)
        self.app.add_url_rule('/vote', None, self.vote, methods=['POST'])

    def set_auth(self, auth):
        self._auth = auth

    def main(self):
        return jsonify(Name=self.bot.user.name, Status='Online' if self.bot.is_ready() else 'Offline', Ping=self.bot.latency * 1000 if self.bot.is_ready() else 0)

    def ping(self):
        return jsonify(Status='Online' if self.bot.is_ready() else 'Offline', Ping=self.bot.latency * 1000 if self.bot.is_ready() else 0)

    def vote(self):
        req_auth = request.headers.get('Authorization')
        if self._auth == req_auth and self._auth is not None:
            data = request.json or request.form or request.args or {}
            if data.get('type', None) == 'upvote':
                event_name = 'vote'
            elif data.get('type', None) == 'test':
                event_name = 'test_vote'
            else:
                return Response(status=401)
            self.bot.dispatch(event_name, data)
            return Response(status=200)
        else:
            return Response(status=401)

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        self._thread = Thread(target=lambda: self.app.run(host, port, debug, load_dotenv=load_dotenv, **options))
        self._thread.setDaemon(True)
        self._thread.start()


class TopGGPoster(TaskPlus):
    def __init__(self, bot: BotPlus, token: str, timer: float = 1800):
        super().__init__(bot, seconds=timer)
        self.token = token
        self.shard_count: Optional[int] = None
        self.shard_id: Optional[int] = None

        self.headers = {
            'User-Agent': __agent__,
            'Content-Type': 'application/json',
            'Authorization': self.token
        }

    @TaskPlus.execute
    def post(self):
        payload = {'server_count': len(self.bot.guilds)}
        if self.shard_count is not None:
            payload["shard_count"] = self.shard_count
        if self.shard_id is not None:
            payload["shard_id"] = self.shard_id
        return post('https://top.gg/api/bots/stats', data=json.dumps(payload), headers=self.headers)


class CogLib:
    def __init__(self, bot: BotPlus):
        self.bot = bot

        self._TopGGTask = None
        self._PSOP = None

    def activate_api(self, import_name, host=None, port=None, vote_auth=None):
        self.bot.api = API(self.bot, import_name)
        self.bot.add_cog(self.bot.api, )
        self.bot.api.set_auth(vote_auth)
        self.bot.api.run(host=host, port=port)
        return self.bot.api

    def activate_topgg_poster(self, token: str, timer: float = 1800):
        self._TopGGTask = TopGGPoster(self.bot, token, timer)
        self._TopGGTask.start()
        return self._TopGGTask

    def disable_topgg_poster(self):
        self._TopGGTask.stop()
