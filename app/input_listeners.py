import os
import sys
from threading import Event, Thread

# Unix-specific imports
if os.name != 'nt':
    import termios
    import tty
    import select


class InputListener:
    def __init__(self):
        self._key_pressed = Event()
        self._input_thread = Thread(target=self._listen, daemon=True)

    def _listen(self):
        if os.name == 'nt':
            # ? Windows implementation (not needed for this specific query but good to keep)
            import msvcrt
            while not self._key_pressed.is_set():
                if msvcrt.kbhit():
                    msvcrt.getch()
                    self._key_pressed.set()
        else:
            # ? Unix/Linux/macOS implementation
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while not self._key_pressed.is_set():
                    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                        sys.stdin.read(1)
                        self._key_pressed.set()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def start(self):
        """Starts the input listening thread."""
        self._input_thread.start()

    def is_key_pressed(self):
        """Returns True if a key has been pressed."""
        return self._key_pressed.is_set()
