import asyncio
from asyncio import Task
from typing import Dict, Optional, Callable, Coroutine, Any


class LooperManager:
    def __init__(self) -> None:
        self._loopers: Dict[str, asyncio.Task] = {}  # 用字典存储 looper 任务
        self._lock = asyncio.Lock()  # 用于确保操作是线程安全的

    async def add_looper(self, label: str, looper_task: Callable[[], Coroutine[Any, Any, None]]) -> None:
        """加入as队列并添加一个新的 looper 到列表"""
        looper_task = asyncio.create_task(looper_task())
        async with self._lock:
            self._loopers[label] = looper_task

    async def remove_looper(self, label: str) -> None:
        """根据标签移除 looper"""
        async with self._lock:
            if label in self._loopers:
                self._loopers[label].cancel()  # 取消任务
                del self._loopers[label]  # 删除 looper 任务

    async def get_looper(self, label: str) -> Optional[asyncio.Task]:
        """根据标签获取 looper"""
        async with self._lock:
            return self._loopers.get(label, None)

    async def list_loopers(self) -> Dict[str, asyncio.Task]:
        """列出所有 looper"""
        async with self._lock:
            return self._loopers.copy()  # 返回一个副本，防止外部修改