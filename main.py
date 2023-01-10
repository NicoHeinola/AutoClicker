
from clicker import Clicker
from icon import Icon
from interface import GUI

if __name__ == "__main__":
    clicker = Clicker()
    gui = GUI(clicker.startClicking, clicker.stopClicking)
    icon = Icon(gui._tk, gui.hide, gui.show)
    gui.mainloop()
j