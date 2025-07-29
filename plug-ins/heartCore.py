import asyncio

from scr.PATH import looper_manager
from scr.util.signalbus import event
from scr.util.logger import Logger

_log = Logger()

async def heart() -> None:
    while True:
        _log.info("Hello")
        await asyncio.sleep(1)


@event("heartHook")
async def hook():
    await looper_manager.add_looper("heart_L",heart)