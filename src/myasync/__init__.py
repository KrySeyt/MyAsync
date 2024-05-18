__all__ = (
    "gather",
    "create_task",
    "sleep",
    "run",
    "Lock",
    "Coroutine",
    "EventLoop",
    "AbstractTask",
    "Task",
    "TaskProxy",
    "IOType",
    "Await",
    "send",
    "recv",
)

import time
from typing import TypeVar

from myasync.loop import (
    AbstractTask,
    Await,
    Coroutine,
    EventLoop,
    IOType,
)
from myasync.task import (
    Task,
    TaskProxy,
)
from myasync.sockets import (
    send,
    recv,
)
from myasync.selector import SelectSelector
from myasync.lock import Lock

T_co = TypeVar("T_co", covariant=True)

loop = EventLoop(SelectSelector())


def sleep(seconds: float = 0) -> Coroutine[None]:
    start_time = time.time()

    while start_time + seconds > time.time():
        yield None


def create_task(coro: Coroutine[T_co]) -> TaskProxy[T_co]:
    coro_task = Task(coro)
    loop.attach_task(coro_task)
    return TaskProxy(coro_task)


def gather(*awaitables: Coroutine[T_co] | AbstractTask[T_co]) -> TaskProxy[None]:
    tasks = []
    for awaitable in awaitables:
        task = awaitable if isinstance(awaitable, AbstractTask) else create_task(awaitable)
        tasks.append(task)

    def gather_coro() -> Coroutine[None]:
        for task in tasks:
            yield from task

        return None

    return create_task(gather_coro())


def run(coro: Coroutine[T_co]) -> None:
    coro_task = Task(coro)
    loop.attach_task(coro_task)
    loop.run()
