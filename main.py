import asyncio
from scr.util.signalbus import bus, load_folder
from scr.PATH import plugins
from scr.util.logger import Logger

_log = Logger()


async def main() -> None:
    # 1) 动态挂起插件
    load_folder(plugins)
    # 2) 广播系统级 startup 信号
    await bus.emit("heartHook")

    # 3) 主循环：每秒发送一条基础信号 raw_data
    semaphore = asyncio.Semaphore(0)  # 初始化信号量为 0，强制阻塞
    await semaphore.acquire()  # 阻塞，直到信号量被释放

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _log.info("检测到CTRL+C，退出程序。")
