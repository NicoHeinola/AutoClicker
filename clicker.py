from threading import Thread
import time
from typing import Dict
import win32api
import win32con
from pygame import time as pg_time

from ctypes import windll, Structure, c_long, byref


class Vector2:
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def queryMousePosition() -> Vector2:
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return Vector2(pt.x, pt.y)


class ClickThread(Thread):
    def __init__(self, interval: float, hold: bool, clickButton: str, clickPos: tuple, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._running: bool = True
        self._interval: float = interval
        self._clickPos: tuple = clickPos
        self._clickButton: str = clickButton
        self._hold: bool = hold

        self._clickFunc = None
        if self._clickButton == "left":
            self._clickFunc = ClickThread._leftClick
        elif self._clickButton == "right":
            self._clickFunc = ClickThread._rightClick
        elif self._clickButton == "middle":
            self._clickFunc = ClickThread._middleClick

    def stop(self) -> None:
        self._running = False

    @staticmethod
    def _leftClick(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    @staticmethod
    def _rightClick(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

    @staticmethod
    def _middleClick(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, x, y, 0, 0)

    @staticmethod
    def _holdLeft(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)

    @staticmethod
    def _holdRight(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)

    @staticmethod
    def _holdMiddle(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, x, y, 0, 0)

    @staticmethod
    def _unholdLeft(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    @staticmethod
    def _unholdRight(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

    @staticmethod
    def _unholdMiddle(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, x, y, 0, 0)

    def _runHold(self) -> None:
        # Get the hold position
        if self._clickPos is None:
            pos: Vector2 = queryMousePosition()
        else:
            pos: Vector2 = Vector2(self._clickPos[0], self._clickPos[1])

        # Check which button user wants to hold and get the correct function for it
        if self._clickButton == "left":
            holdFunc = ClickThread._holdLeft
            unholdFunc = ClickThread._unholdLeft
        elif self._clickButton == "right":
            holdFunc = ClickThread._holdRight
            unholdFunc = ClickThread._unholdRight
        elif self._clickButton == "middle":
            holdFunc = ClickThread._holdMiddle
            unholdFunc = ClickThread._unholdMiddle

        # Start holding
        holdFunc(pos.x, pos.y)

        # Wait until user stops holding
        while self._running:
            time.sleep(0.1)

        # Stop holding mouse
        pos = queryMousePosition()
        unholdFunc(pos.x, pos.y)

    def _runClick(self) -> None:
        clock = pg_time.Clock()
        while True:
            if self._running:
                if self._clickPos is None:
                    pos = queryMousePosition()
                    self._clickFunc(pos.x, pos.y)
                else:
                    self._clickFunc(self._clickPos[0], self._clickPos[1])
            else:
                break
            clock.tick(self._interval)

    def run(self) -> None:
        if self._hold:
            self._runHold()
        else:
            self._runClick()


class MousePosThread(Thread):
    def __init__(self, updateFunc, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._updateFunc = updateFunc
        self._running: bool = True
        self._paused: bool = False

    def stop(self):
        self._running: bool = False
        self._paused = False

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    def run(self) -> None:
        interval: float = 1 / 20
        while True:
            if self._paused:
                time.sleep(0.25)
            else:
                if self._running:
                    if not self._paused:
                        pos: Vector2 = queryMousePosition()
                        self._updateFunc(pos.x, pos.y)
                else:
                    break
                time.sleep(interval)


class Clicker:
    clickThreads: Dict[str, ClickThread] = {}

    def __init__(self) -> None:
        pass

    def stopClicking(self):
        for key in Clicker.clickThreads:
            Clicker.clickThreads[key].stop()
        Clicker.clickThreads = {}

    def startClicking(self, interval: int, clickButton: str, clickPos: tuple = None, hold: bool = False):
        self.stopClicking()

        thread = ClickThread(interval, hold, clickButton, clickPos, daemon=True)  # Clicking thread
        thread.start()

        Clicker.clickThreads[str(len(Clicker.clickThreads))] = thread
