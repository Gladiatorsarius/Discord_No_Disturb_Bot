import os
import signal
import subprocess
import sys
import threading
import time
from threading import Event

BOT_DIR = os.path.dirname(os.path.abspath(__file__))



BOT_FILE = os.path.join(BOT_DIR, "Do_Not_Disturb.py")


RESTART_FILE = os.path.join(BOT_DIR, "restart.txt")
STARTUP_FILE = os.path.join(BOT_DIR, "startup.txt")
SHUTDOWN_FILE = os.path.join(BOT_DIR, "shutdown.txt")

RESTART_EVENT = Event()
SHUTDOWN_EVENT = Event()


def stream_output(pipe):
    for line in iter(pipe.readline, ""):
        if line:
            print(line.rstrip())
    pipe.close()


def start_bot():
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        [sys.executable, "-u", BOT_FILE],
        cwd=BOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        env=env,
        creationflags=flags,
    )

    threading.Thread(target=stream_output, args=(proc.stdout,), daemon=True).start()
    return proc


def watch_for_enter():
    while not SHUTDOWN_EVENT.is_set():
        try:
            input()
        except EOFError:
            time.sleep(1)
            continue
        RESTART_EVENT.set()


def stop_bot(proc):
    if proc is None or proc.poll() is not None:
        return

    try:
        if os.name == "nt":
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            proc.wait(timeout=10)
        else:
            proc.terminate()
            proc.wait(timeout=10)
    except Exception:
        try:
            proc.kill()
            proc.wait()
        except Exception:
            pass


def create_empty_file(path):
    with open(path, "w", encoding="utf-8"):
        pass


def remove_file_if_exists(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def main():
    bot_proc = start_bot()
    shutdown_requested = False
    printed_bot_exit = False
    printed_waiting = False

    print("Bot running. Press Enter or create restart.txt to request shutdown.")
    threading.Thread(target=watch_for_enter, daemon=True).start()

    try:
        while True:
            # Loop 1: normal runtime/restart/startup/exit detection
            while True:
                if RESTART_EVENT.is_set():
                    RESTART_EVENT.clear()

                    create_empty_file(RESTART_FILE)
                    shutdown_requested = True
                    print("Restart signal received. Created restart.txt.")

                    # Do nothing else this cycle after restart signal.
                    time.sleep(1)
                    continue

                if os.path.exists(STARTUP_FILE):

                    if bot_proc is not None and bot_proc.poll() is None:
                        if shutdown_requested:
                            if not printed_waiting:
                                print("startup file detected after restart bot is still running waiting for bot to shutdown")
                                printed_waiting = True
                        else:
                            print("startup file detected but bot still running")
                    else:
                        print("startup.txt found. Bot is not running, starting bot...")
                        time.sleep(5)
                        bot_proc = start_bot()
                        if shutdown_requested:
                            shutdown_requested = False
                        if printed_bot_exit:
                            printed_bot_exit = False
                        if printed_waiting:
                            printed_waiting = False

                    if not shutdown_requested:
                        remove_file_if_exists(STARTUP_FILE)
                        
                

                # Detect bot exit and break into manual startup loop.
                if bot_proc is not None and bot_proc.poll() is not None:
                    if shutdown_requested:
                        if not printed_bot_exit:
                            print("Bot stopped after shutdown signal.")
                            printed_bot_exit = True
                    else:
                        print(
                            "Bot exited unexpectedly Press Enter to start up bot again."
                        )
                        break
                    

                time.sleep(1)

            # Loop 2: wait for Enter, create startup.txt, then go back to Loop 1
            while True:
                if RESTART_EVENT.is_set():
                    RESTART_EVENT.clear()
                    create_empty_file(STARTUP_FILE)
                    print("startup.txt created.")
                    break
                time.sleep(0.2)

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        SHUTDOWN_EVENT.set()
        stop_bot(bot_proc)


if __name__ == "__main__":
    main()