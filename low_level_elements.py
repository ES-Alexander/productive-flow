#!/usr/bin/env python3

import tkinter as tk

class LabelEntry(object):
    ''' Frame storing a Label and an Entry. '''
    def __init__(self, master, label_kwargs={}, entry_kwargs={},
                 vertical=False, row=0, label_col=0, **kwargs):
        '''
        'label_kwargs' is a dict passed to the internal Label widget
        'entry_kwargs' is a dict passed to the internal Entry widget
        'kwargs' are passed to the overarching Frame widget
        '''
        self._master = master
        self._label = tk.Label(self._master, **label_kwargs)
        self._entry = tk.Entry(self._master, takefocus=True, **entry_kwargs)

        self._label.grid(row=row, column=label_col, sticky='news')
        entry_col = label_col + 1
        if vertical:
            self._entry.grid(row=row+1, column=entry_col)
        else:
            self._entry.grid(row=row, column=entry_col)

class FormattedStringVar(tk.StringVar):
    ''' StringVar with optional constant text. '''
    def __init__(self, prefix='', suffix='', format_str='', **kwargs):
        ''' Uses format_str if set, else prefix/suffix. '''
        super().__init__(**kwargs)
        self._prefix = prefix
        self._suffix = suffix
        self._format_str = format_str
        self._value = ''

    def _value_changer(func):
        def func_wrapper(self, *args, **kwargs):
            ''' Sets the display to the current value with the new format. '''
            func(self, *args, **kwargs)
            self.set(self._value)

    @_value_changer
    def set_format_string(self, format_str):
        ''' '''
        self._format_str = format_str

    @_value_changer
    def set_prefix(self, prefix):
        ''' '''
        self._prefix = prefix

    @_value_changer
    def set_suffix(self, suffix):
        ''' '''
        self._suffix = suffix

    @_value_changer
    def set_format(self, prefix='', suffix=''):
        ''' '''
        self._prefix = prefix
        self._suffix = suffix

    def set(self, value):
        ''' '''
        self._value = value
        if self._format_str:
            output = self._value.format(self._format_str)
        else:
            output = self._prefix + value + self._suffix
        super().set(output)

    def get(self):
        ''' '''
        return self._value




