"""
异步信号-事件-行为调度器
—————————————————————————
一个信号-事件-行为调度器：
- 信号（Signal）：用字符串表示；任何代码都可调用 emit() 发送信号
- 事件（Event）：用 @event(signal) 装饰；收到信号后执行回调，可继续 emit()
- 行为（Action）：用 @action(signal) 装饰；作用同上，语义上更多充当“桥梁/管理”

- 使用 asyncio.create_task 触发协程回调，实现并发执行
- emit() 本身亦为协程；事件 / 行为内部可 await bus.emit(...)
"""

from __future__ import annotations
import asyncio
import importlib.util
import inspect
import pathlib
from asyncio import Task
from collections import defaultdict
from typing import Awaitable, Callable, Dict, List, Union, Coroutine, Any

# → 方便类型提示
AsyncOrSync = Union[Callable[..., Awaitable], Callable[..., None]]

class _AsyncDispatcher:
    def __init__(self) -> None:
        self._table: Dict[str, List[AsyncOrSync]] = defaultdict(list)

    # —— 注册回调 ——
    def register(self, signal: str, func: AsyncOrSync) -> None:
        self._table[signal].append(func)

    # —— 触发信号 ——
    async def emit(self, signal: str, *args, **kwargs) -> None:
        if signal not in self._table:
            return
        loop = asyncio.get_running_loop()
        for fn in list(self._table[signal]):
            if inspect.iscoroutinefunction(fn):
                # 协程回调：直接创建任务
                asyncio.create_task(fn(*args, **kwargs))
            else:
                # 同步回调：跑在线程池，保持不阻塞
                loop.run_in_executor(None, fn, *args, **kwargs)

bus = _AsyncDispatcher()

# —— 装饰器 ——
def event(signal: str):
    """事件：被动响应信号；建议写成 async def"""
    def decorator(func: AsyncOrSync):
        bus.register(signal, func)
        return func
    return decorator

def action(signal: str):
    """行为：在“基础信号”与更高层事件之间承上启下"""
    return event(signal)

# —— 动态加载插件文件 ——
def load_folder(folder: str | pathlib.Path) -> None:
    """
    递归导入 folder 下全部 .py 文件，
    使其中用 @event/@action 装饰的函数即时注册到 bus
    """
    folder = pathlib.Path(folder).expanduser().resolve()

    # ★ 路径存在性与类型检查
    if not folder.exists():
        raise FileNotFoundError(f"指定的路径不存在: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"指定的路径不是文件夹: {folder}")

    for path in folder.rglob("*.py"):
        if path.resolve() == pathlib.Path(__file__).resolve():
            continue  # 跳过自身
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # noqa: SLF001