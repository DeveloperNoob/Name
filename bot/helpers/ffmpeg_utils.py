#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import asyncio
import time
import os
import random
from bot import LOGGER


__all__ = [
    'executor',
    'generate_thumbnail_file'
]


logger = LOGGER(__name__)


async def executor(cmd: list):
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=3
    )

    stdout, stderr = await process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()
    return stdout, stderr


async def generate_thumbnail_file(file_path, output_folder):

    os.makedirs(output_folder, exist_ok=True)
    thumb_file = os.path.join(output_folder, "thumb.jpg")
    cmd = [
        "ffmpeg",
        "-ss",
        "0",
        "-i",
        file_path,
        "-vframes",
        "1",
        "-vf",
        "scale=320:-1",
        "-y",
        str(thumb_file),
    ]
    await executor(cmd)

    if not os.path.exists(thumb_file):
        return None
    return thumb_file

