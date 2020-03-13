#!/usr/bin/env python3

from project import Project
from gui_elements import *

class Controller(object):
    ''' '''
    def __init__(self, **kwargs):
        ''' '''
        self._root = tk.Tk()
        self._project = Project('main')
        self._view = MainView(self._root, self._project, **kwargs)
        self._view.grid(sticky='news')

        self._view.connect_stuff()

        self._root.mainloop()

if __name__ == '__main__':
    Controller()
