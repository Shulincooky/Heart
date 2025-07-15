from scr.async_signalbus import event, action, bus
import asyncio

@event("startup")
async def greet() -> None:
    print("🟢 系统启动完成！（async）")

@action("raw_data")
async def process(data: int) -> None:
    print(f"🔧 行为：收到原始数据 {data}")
    # 模拟 I/O / CPU 计算
    await asyncio.sleep(0.3)
    processed = data * 2
    # 继续向下游事件广播
    await bus.emit("data_ready", processed)

@event("data_ready")
async def show_result(result: int) -> None:
    await asyncio.sleep(0.1)
    print(f"🎉 事件：数据处理完成 -> {result}")
