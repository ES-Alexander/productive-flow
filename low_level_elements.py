#!/usr/bin/env python3

import tkinter as tk

class LabelEntry(object):
    ''' Frame storing a Label and an Entry. '''
    def __init__(self, master, label_kwargs={}, entry_kwargs={},
                 vertical=False, row=0, label_col=0, **kwargs):
        '''
        'label_kwargs' is a dict passed to the internal Label widget
        'entry_kwargs' is a dict passed to the internal Entry widget
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

    def set(self, text):
        ''' Set the internal Entry widget text. '''
        self.clear()
        self._entry.insert(0, text)

    def get(self):
        ''' Return the text of the internal Entry widget. '''
        return self._entry.get()

    def clear(self):
        ''' Clear the text of the internal Entry widget. '''
        self._entry.delete(0, tk.END)

    def bind(self, *args, **kwargs):
        ''' Bind the entry widget as specified. '''
        self._entry.bind(*args, **kwargs)

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
        return func_wrapper

    @_value_changer
    def set_format_string(self, format_str):
        ''' Set the internal format string. Overrides prefix/suffix. '''
        self._format_str = format_str

    @_value_changer
    def set_prefix(self, prefix):
        ''' Set the prefix added to the stored value (unless overriden). '''
        self._prefix = prefix

    @_value_changer
    def set_suffix(self, suffix):
        ''' Set the suffix added to the stored value (unless overriden). '''
        self._suffix = suffix

    @_value_changer
    def set_format(self, prefix='', suffix=''):
        ''' Set the prefix and suffix added to the value (unless overriden). '''
        self._prefix = prefix
        self._suffix = suffix

    def set(self, value):
        ''' Set the stored value and update the display. '''
        self._value = value
        if self._format_str:
            output = self._format_str.format(self._value)
        else:
            output = self._prefix + value + self._suffix
        super().set(output)

    def get(self):
        ''' Get the currently stored value. '''
        return self._value


class BetterButton(tk.Button):
    ''' A button which is invoked when 'Enter' is pressed while in focus. '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind('<Return>', lambda e: self.invoke())

class ScrollableFrame(tk.Canvas):
    ''' A scrollable frame widget. '''
    def __init__(self, master, parent_view=None, row=0, column=0, **kwargs):
        ''' Initialise the widget with an optional parent ProjectView. '''
        super().__init__(master, **kwargs)
        self._master = master
        scrollbar = tk.Scrollbar(master, orient='vertical',
                                 command=self.yview)
        self.frame = _ScrollingFrame(self, parent_view)
        self.frame.bind('<Configure>', lambda event=None: self.config(
                scrollregion=self.bbox('all')))

        self.create_window((0,0), window=self.frame, anchor='nw')
        self.config(yscrollcommand=scrollbar.set)
        self.command = lambda event: self.yview_scroll(-event.delta, 'units')
        self.bind('<MouseWheel>', self.command)

        self.grid(row=row, column=column, sticky='nsew')
        scrollbar.grid(row=row, column=column+1, sticky='ns')

class _ScrollingFrame(tk.Frame):
    ''' Frame widget with an optional parent ProjectView. '''
    def __init__(self, master, parent_view=None, **kwargs):
        super().__init__(master, **kwargs)
        self._master = parent_view or master
