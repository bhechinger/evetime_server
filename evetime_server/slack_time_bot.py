#!/usr/bin/env python3
## -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from slacker import Slacker
from pprint import pprint
from datetime import datetime
#from pytz import timezone
import pytz, argparse, locale

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

locale.setlocale(locale.LC_ALL, 'C.UTF-8')
app = Flask(__name__)

parser = argparse.ArgumentParser(description='Send time in UTC plus conversion to requesting user\'s timezone')
parser.add_argument('-c', '--config', help='Config file [default is slack.conf in current dir]')
parser.add_argument('-d', '--debug', help='print debug output', action="store_true")
args = parser.parse_args()

if args.config:
    config_file = args.config
else:
    config_file = '/home/app/config/slack.conf'

config = configparser.ConfigParser()
config.read(config_file)

api_key = config.get('slack', 'api_key')
bot_name = config.get('bot', 'name')
bot_icon = config.get('bot', 'icon')

slack = Slacker(api_key)

@app.route('/')
def index():
    return "Nothing to see here, move along!"

@app.route('/time_bot')
def time_bot_def():
    return "Please RTFM"

@app.route('/time_bot/<req_username>/<req_channel>')
def time_bot(req_username, req_channel):
    # Get users list
    response = slack.users.list()
    users = response.body['members']

    utc = pytz.utc
    req_tz = request.args.get('tz', '')
    req_time = request.args.get('time', '')
    if req_time:
        utc_dt = datetime(2015, 1, 1, int(req_time[:-2]), int(req_time[-2:]))
        fmt = "%H:%M"
    else:
        utc_dt = datetime.utcnow()
        fmt = "%Y-%m-%d %H:%M:%S"

    for user in users:
        if user['name'] == req_username:
            if not req_tz:
                user_tz = pytz.timezone(user['tz'])
                dest_tz = user['tz_label']
            else:
                if req_tz in pytz.common_timezones:
                    user_tz = pytz.timezone(req_tz)
                    dest_tz = req_tz
                else:
                    slack.chat.post_message('#{channel}'.format(channel=req_channel), '@{name}: Invalid time zone: {tz}'.format(name=user['name'], tz=req_tz), username=bot_name, icon_url=bot_icon)
                    return "Sent error message to {u}".format(u=req_username)

            utc_dt = pytz.utc.localize(utc_dt)
            loc_dt = utc_dt.astimezone(user_tz)
            slack.chat.post_message('#{channel}'.format(channel=req_channel), '@{name}: The EVE time is {utc} and in {tz}: {local}'.format(name=user['name'], tz=dest_tz, utc=utc_dt.strftime(fmt), local=loc_dt.strftime(fmt)), username=bot_name, icon_url=bot_icon)

    return "Sent slack message to {u}".format(u=req_username)

if __name__ == '__main__':
        app.run(debug=True)
