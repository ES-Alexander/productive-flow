#!/usr/bin/env python3

# tk, LabelEntry, FormattedStringVar, BetterButton
from low_level_elements import *

# relevant global GUI element and binding variables
from sys import platform
if platform.startswith('darwin'):
    CLICK_CURSOR = 'pointinghand'
    CTRL = lambda key: '<Command-{}>'.format(key)
else:
    CLICK_CURSOR = 'double_arrow'
    CTRL = lambda key: '<Control-{}>'.format(key)

HEADING_FONT = ('Helvetica', 16, 'bold')

MAIN_NAME = '_main' # the intended project to run from


# binding keys
ADD_BIND     = 'add'
FOCUS_BIND   = 'focus'
DELETE_BIND  = 'delete'
SUBMIT_BIND  = 'submit'
RESTORE_BIND = 'restore'


class ProjectViewBase(tk.Frame):
    ''' The base class for displaying a Project and its Sub-Projects.

    While some methods are populated, this class is intended to be abstract
    and should not be initialised directly. Create instances from the
    MainView and ProjectView concrete sub-classes.

    '''
    def __init__(self, master, project, **kwargs):
        ''' Initialise the underlying frame and store the project. '''
        super().__init__(master, **kwargs)
        self._master = master
        self._project = project

    @property
    def parent(self):
        ''' Set 'parent' as an alias of _master. '''
        return self._master

    def __save_project(func):
        ''' A wrapper for functions which should save the internal project. '''
        def func_wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._project.save()
            return result
        return func_wrapper

    def _create_display(self):
        ''' Initialise the display of this view element. '''
        pass

    @__save_project
    def update_project(self, **params):
        ''' Edit the internal project parameters. '''
        self._project.update_params(**params)

    def add_sub_project(self, project):
        ''' Adds the given project to the display. '''
        pass

    @__save_project
    def remove_sub_project(self, project_view):
        ''' Removes the given project from the stored project.

        Subclass must: Remove and return a ProjectView from the display.
        '''
        self._project.remove_sub_project(project_view._project)

    @__save_project
    def create_sub_project(self, **params):
        ''' Create and display a sub-project with given parameters. '''
        self.add_sub_project(self._project.create_sub_project(**params))


class ProjectView(ProjectViewBase):
    ''' The basic display of a project and its sub-projects. '''
    def __init__(self, master, project, bindings, default_show=True,
                 show_complete=True, **kwargs):
        ''' Create a ProjectView for the given Project. '''
        super().__init__(master, project, **kwargs)
        self._bindings      = bindings

        self._show_complete = show_complete
        self._default_show  = default_show
        self.hidden         = False

        self._create_display()

        self._add_bindings()

    def _create_display(self):
        ''' Create the display elements of this view. '''
        self._display_name()
        self._display_due_date()
        self._display_sub_projects()

    def _display_name(self):
        ''' Display the Project name, with appropriate bindings. '''
        self._name = tk.Label(self, text=self._project.name)
        self._name.grid(row=0, column=1, sticky='w')
        self._the_og_bg = self._name.cget('background')
        self._the_og_fg = self._name.cget('foreground')
        self._in_focus = False

        if self._project.complete:
            self.update_name_complete(init=True)
        else:
            self.update_name_not_complete()

    def _display_due_date(self):
        ''' Display the Project's due date, if applicable. '''
        due_date = self._project.get_due_date_str()
        self._due_date = tk.Label(self, text=self._project.get_due_date_str())
        if due_date:
            self._due_date.grid(row=1, column=1, sticky='w')

    def _display_sub_projects(self):
        ''' Display minimisable sub-projects as applicable. '''
        if self._project.sub_projects:
            if hasattr(self, '_spacer'):
                self._spacer.grid_remove()
                del self._spacer
            self._create_sub_project_display()
        else:
            if hasattr(self, '_sub_projects'):
                self._sub_projects.grid_remove()
                self._minimise.grid_remove()
                del self._sub_projects
                del self._minimise
            self._create_spacer_display()

    def _create_sub_project_display(self):
        ''' '''
        self._sub_projects = ProjectsDisplay(self,
                self._project.sub_projects.values(), self._bindings,
                show_complete=self._show_complete)
        self._minimise = tk.Label(self, cursor=CLICK_CURSOR)
        self._minimise.grid(row=0, column=0, sticky='n')
        self.maximise()
        if not self._default_show:
            self.minimise()

    def _create_spacer_display(self):
        ''' '''
        self._spacer = tk.Label(self, text=' '*2)
        self._spacer.bind('<Button-1>', self._bindings[RESTORE_BIND])
        self._spacer.grid(row=0, column=0)

    def _add_bindings(self):
        ''' Add relevant bindings to this ProjectView. '''
        self.bind('<Button-1>', self._bindings[RESTORE_BIND])
        self._name.bind('<Button-1>',
                        lambda event: self._bindings[FOCUS_BIND](self))
        self._name.bind('<Enter>',
                        lambda event: self._name.config(bg='#eeeeee'))
        self._name.bind('<Leave>',
                        lambda event: self._name.config(bg=self._the_og_bg))

    def _toggle_focus(self):
        ''' '''
        if self._in_focus:
            self._in_focus = False
            self._name.config(relief=tk.FLAT)
        else:
            self._in_focus = True
            self._name.config(relief=tk.RIDGE)

    def update_name_complete(self, init=False):
        ''' Update name because project marked as complete. '''
        if self._show_complete:
            self._name.config(fg='green')
            self._name.bind('<Double-Button-1>', self.remove_complete)
        else:
            self.hidden = True
            if not init:
                self.grid_remove()

    def update_name_not_complete(self):
        ''' Update name because project marked as incomplete. '''
        self._name.config(fg=self._the_og_fg)
        self._name.bind('<Double-Button-1>', self.complete)

    def complete(self, event=None):
        ''' Binding for completion of the Project. '''
        self._project.set_complete()
        self._save_update()
        self.update_name_complete()

    def remove_complete(self, event=None):
        ''' Remove complete status from Project. '''
        self._project.complete = False
        self._project.completion_date = None
        self._save_update()
        self.update_name_not_complete()

    def _save_update(self):
        ''' Saves the stored project and refreshes its focus. '''
        self._project.save()
        # toggle focus off then back on refreshed
        for toggle in range(2):
            self._bindings[FOCUS_BIND](self)

    def add_sub_project(self, project):
        ''' Adds the given project to the display.

        Assumes that 'project' is already a sub-project of the stored project.

        '''
        if hasattr(self, '_sub_projects'):
            self._sub_projects.add_project(project)
        else:
            self._display_sub_projects()

    def remove_sub_project(self, project_view):
        ''' Remove and return a ProjectView from the display. '''
        super().remove_sub_project(project_view)
        self._sub_projects.remove_project_view(project_view)
        if self._sub_projects.is_empty():
            self._display_sub_projects()

    def minimise(self, event=None):
        ''' Binding for hiding this Project's sub-projects. '''
        self._minimise.config(text='+')
        self._sub_projects.grid_remove()
        self._minimise.bind('<Button-1>', self.maximise)

    def maximise(self, event=None):
        ''' Binding for showing this Project's sub-projects. '''
        self._minimise.config(text='-')
        self._sub_projects.grid(row=1, column=1, columnspan=1, sticky='w')
        self._minimise.bind('<Button-1>', self.minimise)


class ProjectsDisplay(tk.Frame):
    ''' A display element for a collection of ProjectViews. '''
    def __init__(self, master, projects, bindings, title=None,
                 show_complete=True, **kwargs):
        ''' Create a display widget for the given projects. '''
        super().__init__(master, **kwargs)
        self._master = master
        self._bindings = bindings
        self._show_complete = show_complete

        if title:
            self._title = tk.Label(self, text=title, font=HEADING_FONT)
            self._title.grid(sticky='ew')

        self.bind('<Button-1>', self._bindings[RESTORE_BIND])

        self._project_views = []
        for project in projects:
            self.add_project(project)

        # TODO scrollbars

    def add_project(self, project):
        ''' Add a Project to the display, return the displayed ProjectView. '''
        project_view = ProjectView(self, project, bindings=self._bindings,
                                   show_complete=self._show_complete)
        return self.add_project_view(project_view)

    def add_project_view(self, project_view):
        ''' Add a ProjectView to the display and return it. '''
        if project_view.parent is not self:
            # create new project view with default parameters (maybe bad?)
            #   -> handles tkinter not allowing changed master
            return self.add_project(project_view._project)

        if not project_view.hidden:
            project_view.grid(sticky='w')
        self._project_views.append(project_view)
        return project_view

    def remove_project_view(self, project_view):
        ''' Remove and return a ProjectView from the display. '''
        project_view._name.config(text='waddafuq?')
        project_view.grid_remove()
        self._project_views.remove(project_view)
        return project_view

    def is_empty(self):
        ''' Returns True if not storing any ProjectViews. '''
        return not self.num_projects

    @property
    def num_projects(self):
        ''' Returns the number of ProjectViews stored in this display. '''
        return len(self._project_views)


class ProjectEditor(tk.Frame):
    ''' A widget to edit and create Project instances. '''
    # title formats
    ADD_FORMAT     = 'Adding to {!r}'
    EDIT_FORMAT    = 'Editing {!r}'
    # mode button text
    GOTO_ADD_MODE  = '++'
    GOTO_EDIT_MODE = '\u21e6'

    def __init__(self, master, bindings, **kwargs):
        ''' Create a ProjectEditor widget within master. '''
        super().__init__(master, **kwargs)
        self._master = master
        self._bindings = bindings

        self._create_display()

    def _create_display(self):
        ''' Create and set up the relevant display widgets. '''
        self._create_title()
        self._create_fields()
        self._create_buttons()

    def _create_title(self):
        ''' Create the title widget. '''
        title_frame = tk.Frame(self)
        title_frame.grid(columnspan=2)
        self._title = FormattedStringVar()
        self._title_label = tk.Label(title_frame, textvariable=self._title,
                                     font=HEADING_FONT)
        self._title_entry = tk.Entry(title_frame) # TODO grid when editing title

        self._title_label.grid(row=0)

    def _create_fields(self):
        ''' Create the Project parameter fields, for adding/editing. '''
        self._entries = {}
        for index, value in enumerate(['name', 'details', 'sub_projects',
                                       'due_date', 'precursors', 'duration',
                                       'scheduled_time', 'completion_date']):
            text = value.replace('_', ' ')
            entry = LabelEntry(self, dict(text=text, anchor='e'), row=index+1)
            entry.bind(CTRL('Return'), self._bindings[SUBMIT_BIND])
            entry.bind(CTRL('BackSpace'), self._bindings[DELETE_BIND])
            entry.bind('<FocusOut>', self.__edit_submit)
            self._entries[value] = entry

    def _create_buttons(self):
        ''' Create the buttons to add/delete a project, or change mode. '''
        self._button_frame = tk.Frame(self)
        self._submit_button = BetterButton(self._button_frame, text='\u2713',
                fg='#006600', command=self._bindings[SUBMIT_BIND])
        self._delete_button = BetterButton(self._button_frame, text='X',
                fg='#660000', command=self._bindings[DELETE_BIND])
        self._add_mode_button = BetterButton(self._button_frame, text='',
                                          command=self._bindings[ADD_BIND])

        self._button_frame.grid(sticky='ew')
        self._submit_button.grid(row=0, column=2, sticky='e')
        self._delete_button.grid(row=0, column=1, sticky='e')
        self._add_mode_button.grid(row=0, column=0, sticky='w')

    def get_submission_results(self):
        ''' Extract and return the results of all the data fields. '''
        submission_results = {}
        for name in self._entries:
            entry = self._entries[name]
            result = entry.get()
            if result:
                submission_results[name.replace(' ','_')] = result
        return submission_results

    def display_selection_data(self, data, clear=True):
        ''' Display 'data' in the data fields. '''
        if clear:
            self.clear()
        for name in data:
            self._entries[name].set(data[name])

    def set_edit_mode(self, new_project=None):
        ''' Enter edit mode for the given project, or the current one. '''
        self._title.set_format_string(self.EDIT_FORMAT)
        if new_project:
            self._project = new_project
            self._title.set(new_project.name)

        self.display_selection_data(self._project.get_properties())

        self._add_mode_button.config(text=self.GOTO_ADD_MODE)
        self._add_mode_button.grid()
        self._submit_button.grid_remove()
        self._delete_button.grid()

    def set_add_mode(self, name=None):
        ''' Enter add mode, adding to 'name' project. '''
        # update title
        if name == MAIN_NAME:
            self._title.set_format_string('{}')
            self._title.set('Add Project')
            self._add_mode_button.grid_remove()
        else:
            self._title.set_format_string(self.ADD_FORMAT)
            if name:
                self._title.set(name)
        # clear entries
        self.clear()
        # update buttons
        self._add_mode_button.config(text=self.GOTO_EDIT_MODE)
        self._submit_button.grid()
        self._delete_button.grid_remove()

    def clear(self):
        ''' Clear all data fields. '''
        for entry in self._entries.values():
            entry.clear()

    def __edit_submit(self, event=None):
        ''' Binding to submit if in edit mode. '''
        if self._add_mode_button.cget('text') == self.GOTO_ADD_MODE:
            self._bindings[SUBMIT_BIND]()
