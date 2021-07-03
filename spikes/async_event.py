import asyncio
import contextlib


# https://docs.python.org/3/library/asyncio-sync.html
async def waiter(event, timeout=2.0):
    print('waiting for it ...')

    # await event.wait()

    with contextlib.suppress(asyncio.TimeoutError):
        await asyncio.wait_for(event.wait(), timeout)

    if event.is_set():
        print('... got it!')
    else:
        print("timeout")
    return event.is_set()


async def main():
    # Create an Event object.
    event = asyncio.Event()

    waiter_task1 = asyncio.create_task(waiter(event, 2.0))
    waiter_task2 = asyncio.create_task(waiter(event, 4.0))

    # Sleep for 1 second and set the event.
    await asyncio.sleep(3)
    event.set()

    # Wait until the waiter task is finished.
    await waiter_task1
    await waiter_task2


asyncio.run(main())
