
from threading import Thread
import tkinter as tk
import PIL
from pystray import MenuItem as item
from pystray import Menu
import pystray
from PIL import Image


class Icon:
    def __init__(self, tkWindow, hideCommand=None, showCommand=None) -> None:
        self._tk: tk.Tk = tkWindow
        self._tk.protocol('WM_DELETE_WINDOW', self._hideWindow)

        self._hideCommand = hideCommand
        self._showCommand = showCommand

        self._title = "Auto Clicker"
        try:
            self._image = Image.open("icon.ico")
        except FileNotFoundError:
            print("Could not find icon")
        except PIL.UnidentifiedImageError:
            print("Could not identify image")
        self._menu = Menu(
            item('Show', self._showWindow),
            item('Quit', self._quitWindow)
        )

    def _quitWindow(self):
        self._tk.destroy()
        self._icon.stop()

    def _showWindow(self):
        self._icon.stop()
        self._tk.after(0, self._tk.deiconify())
        if self._showCommand is not None:
            self._showCommand()

    def _hideWindow(self):
        self._tk.withdraw()
        self._icon = pystray.Icon("name", self._image, self._title, self._menu)
        Thread(target=self._icon.run, daemon=True).start()

        if self._hideCommand is not None:
            self._hideCommand()
