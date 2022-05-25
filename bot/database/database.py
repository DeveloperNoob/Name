#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import motor.motor_asyncio # pylint: disable=import-error
from pymongo.collection import Collection # pylint: disable=import-error
# from pymongo.results import UpdateResult 
import datetime

from bot import Config, LOGGER # pylint: disable=import-error


logger = LOGGER(__name__)
CACHE = {}

class Database:

    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(Config.DB_URI)
        self.db = self._client["ThumbnailChangerBot"]
        self.col: Collection = self.db['Settings']

    async def new_user(self, _id, name=None, username=None):
        data = dict(
            _id=_id,
            name=name,
            username=username,
            status=dict(
                active=True,
                joined_date=datetime.date.today().isoformat(),
                last_used_on=datetime.date.today().isoformat()
            ),
            configs=dict(
                as_file=True,
                need_caption=False,
                caption_data=""
            )
        )
        return data


    async def add_user(self, user_id: int):
        data = await self.new_user(user_id)
        await self.col.insert_one(data)
        
        CACHE[str(user_id)] = data
        return True


    async def remove_user(self, user_id: int):
        if CACHE.get(str(user_id)):
            CACHE.pop(str(user_id))
        
        await self.col.delete_one({"_id": user_id})
        return True


    async def get_user(self, user_id: int):

        cache = CACHE.get(str(user_id))
        if cache is not None:
            return cache
       
        user_data = await self.col.find_one({"_id": user_id})
        
        if not user_data:
            await self.add_user(user_id)
            user_data = await self.new_user(user_id)
        
        CACHE[str(user_id)] = user_data
        return user_data


    async def get_configs(self, user_id: int) -> dict:
        # await self.get_user(user_id)
        # return CACHE[str(user_id)]["configs"]
        return (await self.get_user(user_id))["configs"]


    async def get_status(self, user_id: int):
        await self.get_user(user_id)
        return CACHE[str(user_id)]["status"]


    async def update_user(self, user_id: int, name: str, username: str):
        prev = await self.get_user(user_id)
        await self.col.update_one(prev, {"$set":{"name": name, "username": username}})
        return True


    async def update_configs(self, user_id: int, configs: dict):
        try:
            prev = await self.get_user(user_id)
            update = {"$set":{"configs": configs}}
            await self.col.update_one(prev, update)
            CACHE[str(user_id)]["configs"] = configs
        except Exception as e:
            raise e
        return True


    async def update_status(self, user_id: int, status: dict, name=None, username=None):
        prev = await self.get_user(user_id)
        await self.col.update_one(prev, {"$set":{"status": status}})
        CACHE[str(user_id)]["status"] = status
        
        if not (name and username) == None:
            await self.update_user(user_id, name, username)
            CACHE[str(user_id)]["name"] = name
            CACHE[str(user_id)]["username"] = username
        
        return True


