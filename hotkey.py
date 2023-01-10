from threading import Thread
from typing import Dict
import keyboard
import time


class HotkeyThead(Thread):
    def __init__(self, hotkey: str, hotkeyFunc, requireToggle: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._key: str = hotkey
        self._hotkeyFunc = hotkeyFunc
        self._pressed: bool = False
        self._lastKey: str = ""
        self._holding: bool = False
        self._requireToggle = requireToggle
        self._running = True

    def isBeingPressed(self):
        return self._pressed

    def stop(self):
        self._running = False

    def run(self) -> None:
        while self._running:
            time.sleep(1 / 20)
            self._pressed = keyboard.is_pressed(self._key)
            if self._pressed:
                if not self._requireToggle or self._lastKey != self._key:
                    self._hotkeyFunc()
                    self._lastKey = self._key
            else:
                self._lastKey = ""


class HotkeyHandler:
    def __init__(self) -> None:
        self._keys: Dict[str, HotkeyThead] = {}
    
    def startListeningToKey(self, key: str, pressFunc, requireToggle: bool = False):
        self.stopListeningToKey(key)
        
        keyThread = HotkeyThead(key, pressFunc, requireToggle, daemon=True)
        keyThread.start()
        self._keys[key] = keyThread

    def stopListeningToKey(self, key: str):
        if key in self._keys.keys():
            thread: HotkeyThead = self._keys[key]
            thread.stop()
            self._keys.pop(key)
