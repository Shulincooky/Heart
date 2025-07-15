import asyncio
import random
from scr.async_signalbus import bus, load_folder
from scr.PATH import plugins

async def main() -> None:
    # 1) 动态挂起插件
    print(plugins)
    load_folder(plugins)

    # 2) 广播系统级 startup 信号
    await bus.emit("startup")

    # 3) 主循环：每秒发送一条基础信号 raw_data
    try:
        while True:
            num = random.randint(1, 9)
            print(f"\n💡 基础信号：raw_data -> {num}")
            await bus.emit("raw_data", num)
            await asyncio.sleep(1)      # 控制节奏
    except KeyboardInterrupt:
        print("\n⛔️ 停止主循环，退出。")

if __name__ == "__main__":
    asyncio.run(main())
