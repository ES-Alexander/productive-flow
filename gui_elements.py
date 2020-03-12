#!/usr/bin/env python3

import tkinter as tk

class ProjectView(tk.Frame):
    ''' '''
    def __init__(self, master, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master

class ProjectCreator(tk.Frame):
    ''' '''
    def __init__(self, master, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master

class MainView(object):
    ''' '''
    def __init__(self, master, **kwargs):
        ''' '''
        self._master = master

        # create stuff using kwargs
        self._project_views = tk.Frame(self._master)
        self._project_view = ProjectView(self._project_views)

        # grid stuff
        self._project_views.grid()
        self._project_view.grid()

    def connect_stuff(self, **things_funcs):
        ''' Called externally '''
        pass



