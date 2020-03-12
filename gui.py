#!/usr/bin/env python3

from project import Project
from gui_elements import *

class Controller(object):
    ''' '''
    def __init__(self, **kwargs):
        ''' '''
        self._root = tk.Tk()
        self._view = MainView(self._root, **kwargs)

        self._view.connect_stuff()

        self._root.mainloop()

if __name__ == '__main__':
    Controller()
