"""MIT License

Copyright (c) 2023 EvieePy, ezstarr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import logging
import pathlib

import aiohttp
import asyncpg
import discord
import tomllib
from discord.ext import commands

from .logs import Handler


with open("config.toml", "rb") as fp:
    CONFIG = tomllib.load(fp)


logger: logging.Logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    # noinspection PyUnresolvedReferences,PyDunderSlots
    def __init__(
        self, *, session: aiohttp.ClientSession, pool: asyncpg.Pool
    ) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.session = session
        self.pool = pool

        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or("t! ", "t!"),
        )
        discord.utils.setup_logging(
            handler=Handler(level=CONFIG["LOGGING"]["level"])
        )

    async def setup_hook(self) -> None:
        modules: list[str] = [
            f"{p.parent}.{p.stem}"
            for p in pathlib.Path("modules").glob("*.py")
        ]
        for module in modules:
            await self.load_extension(module)

        logger.info(f"Loaded ({len(modules)}) modules.")

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
