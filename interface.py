import os
from threading import Thread
import tkinter as tk
from tkinter import DISABLED, TclError, ttk
import tkinter
from tkinter.font import NORMAL

import PIL

from clicker import MousePosThread
from hotkey import HotkeyHandler


class NumberEntry(ttk.Entry):
    def __init__(self, master=None, tkVariable: tk.Variable = None, min: int = None, max: int = None, *args, **kwargs):
        if tkVariable is None:
            self._var: tk.Variable = tk.StringVar(0)
        else:
            self._var = tkVariable

        ttk.Entry.__init__(self, master, textvariable=self._var, **kwargs)
        self._old_value: str = ""
        self._var.trace('w', lambda a, b, c: self._check())
        self._min: int = min
        self._max: int = max

    def _check(self):
        if self._var.get().isnumeric():
            num: int = int(self._var.get())
            if self._min is not None and num < self._min:
                self._var.set(self._min)
            elif self._max is not None and num > self._max:
                self._var.set(self._max)

            self._old_value = self._var.get()
        elif self._var.get() == "":
            self._old_value = self._var.get()
        else:
            self._var.set(self._old_value)


class CharacterEntry(ttk.Entry):
    def __init__(self, master=None, tkVariable: tk.Variable = None, *args, **kwargs):
        if tkVariable is None:
            self._var: tk.Variable = tk.StringVar()
        else:
            self._var = tkVariable

        ttk.Entry.__init__(self, master, textvariable=self._var, **kwargs)
        self._var.trace('w', lambda a, b, c: self._check())

    def _check(self):
        if len(self._var.get()) > 1:
            self._var.set(self._var.get()[len(self._var.get()) - 1])


class GUI:
    def __init__(self, startClickingFunc, stopClickingFunc) -> None:
        self._tk = tk.Tk()
        try:
            self._tk.iconbitmap("icon.ico")
        except tk.TclError:
            print("Could not load icon.ico")
        except PIL.UnidentifiedImageError:
            print("Could not identify image")

        self._tk.title("Auto Clicker")
        self._tk.minsize(650, 0)
        self._tk.resizable(False, False)
        self._tk.bind_all("<Button-1>", lambda event: event.widget.focus_set())

        # Tk elements
        self._startButton: ttk.Button = None
        self._stopButton: ttk.Button = None

        # TK Settings
        self._intervalVar = tk.StringVar()
        self._intervalVar.set("1000")
        self._cpsVar = tk.StringVar()
        self._cpsVar.set("1")

        self._startkeyVar = tk.StringVar()
        self._stopkeyVar = tk.StringVar()
        self._togglekeyVar = tk.StringVar()
        self._startkeyVar.set("g")
        self._stopkeyVar.set("h")
        self._togglekeyVar.set("j")

        self._timeFormatVar = tk.StringVar()
        self._timeFormatVar.set("cps")

        self._clickButtonVar = tk.StringVar()
        self._clickButtonVar.set("left")

        self._clickActionVar = tk.StringVar()
        self._clickActionVar.set("click")

        self._clickposVar = tk.StringVar()
        self._clickposVar.set("current")
        self._clickXVar = tk.StringVar()
        self._clickYVar = tk.StringVar()
        self._clickXVar.set("0")
        self._clickYVar.set("0")

        # Hotkeys
        self._startHotkey: str = ""
        self._stopHotkey: str = ""
        self._toggleHotkey: str = ""

        # Functions
        self._startClickingFunc = startClickingFunc
        self._stopClickingFunc = stopClickingFunc

        # Mouse position
        self._mousePosVarText = tk.StringVar()
        self._mousePosVarText.set("Position: ?, ?")
        self._mousePosThread: MousePosThread = MousePosThread(lambda x, y: self._mousePosVarText.set(f"Position: {x}, {y}"), daemon=True)
        self._mousePosThread.pause()
        self._mousePosThread.start()
        # Clicking related
        self._clicking: bool = False

        # Hotkeys
        self._hotkeyHandler = HotkeyHandler()

        self._createGUI()
        self._restartHotkeys()

    def _createGUI(self):
        try:
            self._tk.call("source", os.path.join("themes", "azure", "azure.tcl"))
            self._tk.call("set_theme", "dark")
        except Exception as e:
            print("Could not load theme")

        style = ttk.Style(self._tk)
        style.configure("LargeButton.TButton", width=37)

        framePadding: int = 10
        frameInnerPadding: int = 20

        mainFrame = ttk.Frame(self._tk)
        mainFrame.pack(pady=framePadding, padx=20, fill=tk.X)

        # Interval settings
        intervalLabelFrame: ttk.Labelframe = ttk.Labelframe(mainFrame, text="Click Interval")
        intervalLabelFrame.pack(fill=tk.X, pady=(0, framePadding))

        intervalFrame: ttk.Frame = ttk.Frame(intervalLabelFrame)
        intervalFrame.pack(padx=frameInnerPadding, pady=frameInnerPadding)

        timeFrame: ttk.Frame = ttk.Frame(intervalFrame)
        timeFrame.pack(side=tk.LEFT, padx=(0, 20))
        timeFormatFrame: ttk.Frame = ttk.Frame(intervalFrame)
        timeFormatFrame.pack(side=tk.LEFT, padx=(20, 0))

        msFrame = ttk.Frame(timeFrame)
        ttk.Label(msFrame, text="Click Interval (ms)").pack(anchor=tk.W)
        NumberEntry(msFrame, self._intervalVar, 1).pack()
        cpsFrame = ttk.Frame(timeFrame)
        cpsFrame.pack()
        ttk.Label(cpsFrame, text="Clicks Per Second").pack(anchor=tk.W)
        NumberEntry(cpsFrame, self._cpsVar, 1).pack()

        def showMS():
            msFrame.pack()
            cpsFrame.pack_forget()

        def showCPS():
            cpsFrame.pack()
            msFrame.pack_forget()

        ttk.Label(timeFormatFrame, text="Time Format").pack()
        ttk.Radiobutton(timeFormatFrame, text="Clicks per second", variable=self._timeFormatVar, value="cps", command=showCPS).pack(anchor=tk.W)
        ttk.Radiobutton(timeFormatFrame, text="Milliseconds", variable=self._timeFormatVar, value="ms", command=showMS).pack(anchor=tk.W)

        rowFrame1: ttk.Frame = ttk.Frame(mainFrame)
        #rowFrame1.columnconfigure(0, weight=1)
        #rowFrame1.columnconfigure(1, weight=1)
        #rowFrame1.columnconfigure(2, weight=1)
        rowFrame1.pack(fill=tk.X, pady=framePadding)

        # Hotkey settings
        hotkeyLabelFrame: ttk.Frame = ttk.Labelframe(rowFrame1, text="Hotkey Settings")
        hotkeyLabelFrame.pack(side=tk.LEFT)
        hotkeyFrame: ttk.Frame = ttk.Frame(hotkeyLabelFrame)
        hotkeyFrame.pack(padx=frameInnerPadding, pady=frameInnerPadding)

        ttk.Label(hotkeyFrame, text="Start Key").pack(anchor=tk.W)
        CharacterEntry(hotkeyFrame, self._startkeyVar).pack(pady=(0, 10))
        ttk.Label(hotkeyFrame, text="Stop Key").pack(anchor=tk.W)
        CharacterEntry(hotkeyFrame, self._stopkeyVar).pack(pady=(0, 10))
        ttk.Label(hotkeyFrame, text="Toggle Key").pack(anchor=tk.W)
        CharacterEntry(hotkeyFrame, self._togglekeyVar).pack(pady=(0, 10))
        ttk.Button(hotkeyFrame, text="Assign Hotkeys", command=self._restartHotkeys).pack()

        # Click button settings
        clickTypeParentFrame: ttk.Frame = ttk.Frame(rowFrame1)
        clickTypeParentFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        clicktypeLabelFrame: ttk.Frame = ttk.Labelframe(clickTypeParentFrame, text="Mouse Button Settings")
        clicktypeLabelFrame.pack(side=tk.TOP)
        clicktypeInnerFrame: ttk.Frame = ttk.Frame(clicktypeLabelFrame)
        clicktypeInnerFrame.pack(padx=frameInnerPadding, pady=frameInnerPadding)
        clickbuttonFrame: ttk.Frame = ttk.Frame(clicktypeInnerFrame)
        clickbuttonFrame.pack()

        ttk.Label(clickbuttonFrame, text="Mouse Button").pack(anchor=tk.W)
        ttk.Radiobutton(clickbuttonFrame, text="Left Click", variable=self._clickButtonVar, value="left").pack(anchor=tk.W)
        ttk.Radiobutton(clickbuttonFrame, text="Right Click", variable=self._clickButtonVar, value="right").pack(anchor=tk.W)
        ttk.Radiobutton(clickbuttonFrame, text="Middle Click", variable=self._clickButtonVar, value="middle").pack(anchor=tk.W)

        clicktypeFrame: ttk.Frame = ttk.Frame(clicktypeInnerFrame)
        clicktypeFrame.pack(pady=(framePadding, 0), fill=tk.X)

        def changeToHold():
            for child in timeFormatFrame.winfo_children():
                child.configure(state=tk.DISABLED)
            for child in cpsFrame.winfo_children():
                child.configure(state=tk.DISABLED)
            for child in msFrame.winfo_children():
                child.configure(state=tk.DISABLED)

        def changeToClick():
            for child in timeFormatFrame.winfo_children():
                child.configure(state=tk.NORMAL)
            for child in cpsFrame.winfo_children():
                child.configure(state=tk.NORMAL)
            for child in msFrame.winfo_children():
                child.configure(state=tk.NORMAL)

        ttk.Label(clicktypeFrame, text="Button Action").pack(anchor=tk.W)
        ttk.Radiobutton(clicktypeFrame, text="Click", variable=self._clickActionVar, value="click", command=changeToClick).pack(anchor=tk.W)
        ttk.Radiobutton(clicktypeFrame, text="Hold", variable=self._clickActionVar, value="hold", command=changeToHold).pack(anchor=tk.W)

        # Click position setting
        def changeToPick():
            mouseX.config(state=tk.NORMAL)
            mouseY.config(state=tk.NORMAL)
            self._startUpdatingMousePos()

        def changeToCurrent():
            mouseX.config(state=tk.DISABLED)
            mouseY.config(state=tk.DISABLED)
            self._stopUpdatingMousePos()

        clickPositionLabelFrame: ttk.Frame = ttk.Labelframe(rowFrame1, text="Mouse Position Settings")
        clickPositionLabelFrame.pack(side=tk.RIGHT)
        clickPositionFrame: ttk.Frame = ttk.Frame(clickPositionLabelFrame)
        clickPositionFrame.pack(padx=frameInnerPadding, pady=frameInnerPadding)
        ttk.Label(clickPositionFrame, text="Mouse Position").pack(anchor=tk.W)
        ttk.Radiobutton(clickPositionFrame, text="Use Current Position", variable=self._clickposVar, value="current", command=changeToCurrent).pack(anchor=tk.W)
        ttk.Radiobutton(clickPositionFrame, text="Pick a Position", variable=self._clickposVar, value="pick", command=changeToPick).pack(anchor=tk.W)

        positionLabel = ttk.Label(clickPositionFrame, textvariable=self._mousePosVarText, state=tk.DISABLED)
        positionLabel.pack(anchor=tk.W, pady=10)

        mouseX = NumberEntry(clickPositionFrame, self._clickXVar, 0, state=tk.DISABLED)
        mouseY = NumberEntry(clickPositionFrame, self._clickYVar, 0, state=tk.DISABLED)

        ttk.Label(clickPositionFrame, text="Mouse X").pack(anchor=tk.W)
        mouseX.pack()
        ttk.Label(clickPositionFrame, text="Mouse Y").pack(anchor=tk.W)
        mouseY.pack()

        # Save button
        # ttk.Button(mainFrame, style="Accent.TButton",  text="Save", command=self._saveSettings).pack(pady=10)

        # Other buttons
        buttonsFrame = ttk.Frame(mainFrame)
        buttonsFrame.pack(pady=(framePadding, 0), fill=tk.X)

        self._startButton = ttk.Button(buttonsFrame, state=tk.NORMAL, text="Start Clicking", command=self._startClicking, style="LargeButton.TButton")
        self._stopButton = ttk.Button(buttonsFrame, state=tk.DISABLED, text="Stop Clicking", command=self._stopClicking, style="LargeButton.TButton")
        self._startButton.pack(side=tk.LEFT)
        self._stopButton.pack(side=tk.RIGHT)

    @staticmethod
    def _cpsToInterval(cps: float):
        return 1.0 / cps

    @staticmethod
    def _intervalToCPS(interval: float):
        return 1000 / interval

    def _getInterval(self) -> float:
        try:
            if self._timeFormatVar.get() == "cps":
                interval: float = float(self._cpsVar.get())
            elif self._timeFormatVar.get() == "ms":
                interval: float = self._intervalToCPS(float(self._intervalVar.get()))
            if interval == 0:
                interval = 1
                self._intervalVar.set(1000)
                self._cpsVar.set(1)
        except ValueError:
            interval = 1
            self._intervalVar.set(1000)
            self._cpsVar.set(1)
        return interval

    def _getClickButton(self) -> str:
        return self._clickButtonVar.get()

    def _isHolding(self) -> bool:
        action: str = self._clickActionVar.get()
        if action == "click":
            return False
        return True

    def hide(self):
        self._stopUpdatingMousePos()

    def show(self):
        self._startUpdatingMousePos()

    def _getClickPos(self) -> tuple:
        if self._clickposVar.get() == "current":
            return None
        try:
            x: int = int(self._clickXVar.get())
        except ValueError:
            x: int = 0
        try:
            y: int = int(self._clickYVar.get())
        except ValueError:
            y: int = 0

        return (x, y)

    def _restartHotkeys(self):
        def startHotkey(newHotkey: str, oldHotkey: str, command):
            if newHotkey != oldHotkey:
                self._hotkeyHandler.stopListeningToKey(oldHotkey)
                if newHotkey != "":
                    self._hotkeyHandler.startListeningToKey(newHotkey, command, True)

        startHotkey(self._startkeyVar.get(), self._startHotkey, self._startClicking)
        self._startHotkey = self._startkeyVar.get()
        startHotkey(self._stopkeyVar.get(), self._stopHotkey, self._stopClicking)
        self._stopHotkey = self._stopkeyVar.get()
        startHotkey(self._togglekeyVar.get(), self._toggleHotkey, self._toggleClicking)
        self._toggleHotkey = self._togglekeyVar.get()

    def _toggleClicking(self):
        self._clicking = not self._clicking
        if self._clicking:
            self._startClicking()
        else:
            self._stopClicking()

    def _startUpdatingMousePos(self):
        if self._clickposVar.get() != "current" and self._startButton.cget("state") != tk.DISABLED:
            self._mousePosThread.unpause()

    def _stopUpdatingMousePos(self):
        self._mousePosThread.pause()
        self._mousePosVarText.set("Position: ?, ?")

    def _stopClicking(self):
        # self._restartHotkeys()
        self._startButton.config(state=tk.NORMAL)
        self._stopButton.config(state=tk.DISABLED)
        self._stopClickingFunc()

        self._startUpdatingMousePos()

    def _startClicking(self):
        # self._restartHotkeys()
        # Makes sure that program isn't clicking already
        print(self._startButton["state"], tk.NORMAL, self._startButton["state"] == tk.NORMAL)
        if str(self._startButton["state"]) == tk.NORMAL:
            self._startButton.config(state=tk.DISABLED)
            self._stopButton.config(state=tk.NORMAL)

            self._stopUpdatingMousePos()

            Thread(daemon=True, target=lambda: self._startClickingFunc(self._getInterval(), self._getClickButton(), self._getClickPos(), self._isHolding())).start()

    def mainloop(self):
        self._tk.mainloop()
