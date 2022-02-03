# !/usr/bin/env python3
import os
import glob
import string
import time
import asyncio
from contextlib import suppress
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

enable_debug = False
sort_by_date_then_patreon = False
number_of_parallel_downloads = int(os.environ.get('TG_MAX_PARALLEL', 16))
watch_path = r"Z:\TelegramDownloads"  # this should be your telegram download directory
download_path = r"Z:\sortedprinterdownloads"  # this is the place you want to move the files to
# Create a queue that we will use to store our downloads.
queue = asyncio.Queue(30)

if enable_debug:
    logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)


def log(string):
    logging.info(string)


def logDebug(string):
    logging.debug(string)


def logError(string):
    logging.error(string)


def move_existing_files():
    log("moving existing files")
    files = glob.glob("%s/*" % watch_path)
    for file in files:
        checkAccess(file)
        move_file(file)


def move_file(filepath):
    try:
        if "_" in filepath:
            dashPath = filepath.replace("_","-")
            os.rename(filepath, dashPath.lower())
            filepath = dashPath
        filename = os.path.basename(filepath)
        os.makedirs(download_path, exist_ok=True)
        if "monthly" in filename.lower() and "-" in filename:
            split = filename.split('-')
            patreon = split[1]
            monthly_path = os.path.join(download_path, "monthly")
            if sort_by_date_then_patreon:
                date = os.path.splitext(split[2])[0]
                monthly_path = os.path.join(monthly_path, date.strip())
            patreon_path = os.path.join(monthly_path, patreon.strip())
            os.makedirs(patreon_path.lower(), exist_ok=True)
            final_path = os.path.join(patreon_path, filename)

        elif "kickstarter" in filename.lower() and "-" in filename:
            kickstarter_path = os.path.join(download_path, "kickstarter")
            os.makedirs(kickstarter_path.lower(), exist_ok=True)
            final_path = os.path.join(kickstarter_path, filename)

        elif "trove" in filename.lower() and "-" in filename:
            split = filename.split('-')
            creator = split[1]
            trove_path = os.path.join(download_path, "trove")
            creator_path = os.path.join(trove_path, creator.strip())
            os.makedirs(creator_path.lower(), exist_ok=True)
            final_path = os.path.join(creator_path, filename)

        elif "warhammer+" in filename.lower() and "-" in filename:
            split = filename.split('-')
            creator = split[1]
            trove_path = os.path.join(download_path, "warhammer+")
            creator_path = os.path.join(trove_path, creator.strip())
            os.makedirs(creator_path.lower(), exist_ok=True)
            final_path = os.path.join(creator_path, filename)

        else:
            unsorted_path = os.path.join(download_path, "unsorted")
            os.makedirs(unsorted_path.lower(), exist_ok=True)
            final_path = os.path.join(unsorted_path, filename)

        os.rename(filepath, final_path.lower())
        os.chmod(final_path.lower(), 0o777)
        log("[%s] Successfully moved to %s" % (filepath, final_path))
    except Exception as e:
        logError("exception while moving file %s :\n%s" % (filepath, e))


def checkAccess(f):
    runs = 0
    while True: 
        if(runs > 1000):
            logError('timeout during checkaccess: %s never became unblocked' % f)
            break
        waslocked = False
        if os.path.exists(f):
            try:
                os.rename(f, f)
                if(waslocked):
                    time.sleep(5) #wait a bit extra just to be sure
                break
            except OSError as e:
                waslocked = True
                time.sleep(5)  # wait a few seconds and check again
        else:
            logError('error during checkaccess: file not found %s' % f)
            break
        runs+=1


def checkSize(f):
    historicalSize = -1
    while (historicalSize != os.path.getsize(f) or historicalSize == 0):
        historicalSize = os.path.getsize(f)
        time.sleep(15)


async def worker(name):
    while True:
        # Get a "work item" out of the queue.
        event = await queue.get()
        if event.event_type == 'created':
            f = event.src_path
            log('%s checking access for %s' % (name,f))
            checkAccess(f) #check if the file can be renamed, if its locked we'll wait till its unlocked
            #  file is ready to be moved
            log('%s moving %s' % (name,f))
            move_file(event.src_path)

        # Notify the queue that the "work item" has been processed.
        queue.task_done()


async def handler(update):
    if update.event_type == 'created':
        await queue.put(update)


class SomeEventHandler(FileSystemEventHandler):
    def __init__(self, loop, *args, **kwargs):
        self._loop = loop
        super().__init__(*args, **kwargs)

    def on_any_event(self, event):
        asyncio.run_coroutine_threadsafe(handler(event), self._loop)

if(os.path.exists(watch_path) is False):
    log("watch path %s not found",watch_path)
if(os.path.exists(download_path) is False):
    log("download path %s not found",download_path)

move_existing_files()
loop = asyncio.get_event_loop()

event_handler = SomeEventHandler(loop)
observer = Observer()
observer.schedule(event_handler, watch_path, recursive=True)
observer.start()

try:
    tasks = []
    for i in range(number_of_parallel_downloads):
        loop = asyncio.get_event_loop()
        task = loop.create_task(worker(f'worker-{i}'))
        tasks.append(task)
    loop.run_forever()
except KeyboardInterrupt:
    observer.stop()
    for task in asyncio.all_tasks():
        task.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(task)
finally:
    loop.close()
    observer.join()
