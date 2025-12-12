#!/usr/bin/env python3
"""
AutoTyper - Background Typing Tool
Reads script.txt from same folder.
Asks user for:
- hotkeys: START, PAUSE, RESUME, STOP
- typing speed
- randomness

Perfect for VSCode timelapse typing videos or any other Typing TimeLapses
"""

import sys, os, time, random, threading
import keyboard
import pyautogui

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE = get_base_path()
SCRIPT_PATH = os.path.join(BASE, "script.txt")

if not os.path.exists(SCRIPT_PATH):
    print("ERROR: script.txt not found in folder:", BASE)
    input("Press Enter to exit...")
    sys.exit(1)

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    TEXT = f.read()

if len(TEXT.strip()) == 0:
    print("ERROR: script.txt is empty.")
    input("Press Enter to exit...")
    sys.exit(1)

def choose_hotkey(name, options):
    print(f"\nSelect {name} Hotkey:")
    for i, opt in enumerate(options, 1):
        print(f" {i}) {opt}")
    while True:
        choice = input("Choose option: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice)-1]
        print("Invalid choice. Try again.")

def choose_float(label, default):
    while True:
        val = input(f"{label} (default {default}): ").strip()
        if val == "":
            return float(default)
        try:
            return float(val)
        except:
            print("Invalid number. Try again.")

print("\n==== AutoTyper Configuration ====\n")

START_KEY  = choose_hotkey("START",  ["ctrl+alt+s", "ctrl+shift+s", "F8"])
PAUSE_KEY  = choose_hotkey("PAUSE",  ["ctrl+alt+p", "F9"])
RESUME_KEY = choose_hotkey("RESUME", ["ctrl+alt+r", "F10"])
STOP_KEY   = choose_hotkey("STOP",   ["ctrl+alt+x", "F12"])

BASE_CPS     = choose_float("Typing speed (characters per second)", 10.0)
RANDOM_FACTOR = choose_float("Randomness factor (0.0 - 1.0)", 0.30)

print("\nConfiguration complete. Launching AutoTyper...")


class AutoTyper:
    def __init__(self, text, base_cps, randomness):
        self.text = text
        self.base_delay = 1.0 / base_cps
        self.randomness = randomness
        self.index = 0

        self.running = threading.Event()
        self.paused = threading.Event()
        self.stop_flag = threading.Event()

        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def worker(self):
        while True:
            self.running.wait()

            if self.stop_flag.is_set():
                self.index = 0
                self.running.clear()
                self.paused.clear()
                continue

            if self.paused.is_set():
                time.sleep(0.05)
                continue

            if self.index >= len(self.text):
                self.running.clear()
                continue

            ch = self.text[self.index]
            self.index += 1

            pyautogui.write(ch)

            base = self.base_delay
            jitter = random.uniform(-base * self.randomness, base * self.randomness)
            delay = max(0.001, base + jitter)

            time.sleep(delay)

    # CONTROL FUNCTIONS
    def start(self):
        self.paused.clear()
        self.running.set()

    def pause(self):
        self.paused.set()

    def resume(self):
        self.paused.clear()
        self.running.set()

    def stop(self):
        self.stop_flag.set()
        time.sleep(0.1)
        self.stop_flag.clear()
        self.running.clear()
        self.paused.clear()
        self.index = 0


typer = AutoTyper(TEXT, BASE_CPS, RANDOM_FACTOR)


keyboard.add_hotkey(START_KEY,  lambda: (print("START"), typer.start()))
keyboard.add_hotkey(PAUSE_KEY,  lambda: (print("PAUSED"), typer.pause()))
keyboard.add_hotkey(RESUME_KEY, lambda: (print("RESUMED"), typer.resume()))
keyboard.add_hotkey(STOP_KEY,   lambda: (print("STOPPED"), typer.stop()))

print("\nAutoTyper Ready.")
print("Click inside VS Code or target window, then press your START hotkey.")
print("Press CTRL+C to exit anytime.\n")


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting...")
    sys.exit(0)