#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import motor.motor_asyncio # pylint: disable=import-error
import datetime

from typing import Union
from bot import Config, LOGGER # pylint: disable=import-error


logger = LOGGER(__name__)


class Database:

    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(Config.DB_URI)
        self.db = self._client["RenameBot"]
        self.col = self.db["Thumbnails"]


    async def add_thumb(self, user_id: int, file_id: str) -> bool:

        try:
            await self.col.update_one({"_id": user_id}, {"$set": {"file_id": file_id}}, upsert = True)
            return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            return False


    async def get_thumb(self, user_id: int) -> Union[dict, None]:

        thumb = await self.col.find_one({"_id": user_id})
        if isinstance(thumb, dict):
            return thumb["file_id"]
        else:
            return None


    async def del_thumb(self, user_id: int) -> bool:
        await self.col.delete_one({"_id": user_id})
        return True
    

