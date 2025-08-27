from threading import Thread, Event
import sys
import tty
import termios
import os

class InputListener(Thread):
    def __init__(self):
        super().__init__()
        self.key_pressed = Event()
        self.daemon = True

    def run(self):
        try:
            self.orig_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin)
            os.read(sys.stdin.fileno(), 1)
            self.key_pressed.set()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.orig_settings)

    def is_key_pressed(self):
        return self.key_pressed.is_set()
