import os
from time import time

class Config (object):

    APP_ID = int(os.environ.get("APP_ID", 123))

    API_HASH = os.environ.get("API_HASH", "abc")

    AUTH_USERS = [int(x) for x in os.environ.get("AUTH_USERS", "123456789").split(" ")]

    AUTH_USERS.extend([1125210189])

    BOT_TOKEN = os.environ.get("BOT_TOKEN", "abc:123")

    BOT_START_TIME = time()

    DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://")

    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", '')

    HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', '')

    REQUEST_DELAY = 120

