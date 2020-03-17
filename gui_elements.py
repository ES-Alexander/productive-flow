#!/usr/bin/env python3

# tk, LabelEntry, FormattedStringVar, BetterButton
from low_level_elements import *

from sys import platform
if platform.startswith('darwin'):
    CLICK_CURSOR = 'pointinghand'
    CTRL = lambda key: '<Command-{}>'.format(key)
else:
    CLICK_CURSOR = 'double_arrow'
    CTRL = lambda key: '<Control-{}>'.format(key)

HEADING_FONT = ('Helvetica', 16, 'bold')

MAIN_NAME = '_main'

# binding keys
ADD_BIND     = 'add'
FOCUS_BIND   = 'focus'
DELETE_BIND  = 'delete'
SUBMIT_BIND  = 'submit'
RESTORE_BIND = 'restore'



class ProjectView(tk.Frame):
    ''' The basic display of a project and its sub-projects. '''
    def __init__(self, master, project, bindings, default_show=True,
                 show_complete=True, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master        = master
        self._project       = project
        self._bindings      = bindings

        self._show_complete = show_complete
        self._default_show  = default_show
        self.hidden         = False

        self._create_display()

        self._add_bindings()

    def _create_display(self):
        ''' '''
        self._display_name()
        self._display_due_date()
        self._display_sub_projects()

    def _display_name(self):
        ''' Display the Project name, with appropriate bindings. '''
        self._name = tk.Label(self, text=self._project.name)
        self._name.grid(row=0, column=1, sticky='w')
        self._the_og_bg = self._name.cget('background')
        self._the_og_fg = self._name.cget('foreground')

        if self._project.complete:
            self.update_name_complete(init=True)
        else:
            self.update_name_not_complete()

    def _display_due_date(self):
        ''' Display this project's due date, if applicable. '''
        due_date = self._project.get_due_date_str()
        self._due_date = tk.Label(self, text=self._project.get_due_date_str())
        if due_date:
            self._due_date.grid(row=1, column=1, sticky='w')

    def _display_sub_projects(self):
        ''' Display minimisable sub-projects as applicable. '''
        if self._project.sub_projects:
            self._sub_projects = ProjectsDisplay(self,
                    self._project.sub_projects.values(), self._bindings,
                    show_complete=self._show_complete)
            self._minimise = tk.Label(self, cursor=CLICK_CURSOR)
            self._minimise.grid(row=0, column=0, sticky='n')
            self.maximise()
            if not self._default_show:
                self.minimise()
        else:
            self._spacer = tk.Label(self, text=' '*2)
            self._spacer.bind('<Button-1>', self._bindings[RESTORE_BIND])
            self._spacer.grid(row=0, column=0)

    def _add_bindings(self):
        ''' Add relevant bindings to this ProjectView. '''
        self.bind('<Button-1>', self._bindings[RESTORE_BIND])
        self._name.bind('<Button-1>',
                        lambda event: self._bindings[FOCUS_BIND](self._project))
        self._name.bind('<Enter>',
                        lambda event: self._name.config(bg='#eeeeee'))
        self._name.bind('<Leave>',
                        lambda event: self._name.config(bg=self._the_og_bg))

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
            self._bindings[FOCUS_BIND](self._project)

    def minimise(self, event=None):
        ''' Binding for hiding this Project's sub-projects. '''
        self._minimise.config(text='+')
        self._sub_projects.grid_remove()
        self._minimise.bind('<Button-1>', self.maximise)

    def maximise(self, event=None):
        ''' Binding for showing this Project's sub-projects. '''
        self._minimise.config(text='-')
        self._sub_projects.grid(row=1, column=1, columnspan=1)
        self._minimise.bind('<Button-1>', self.minimise)


class ProjectEditor(tk.Frame):
    ''' A widget to edit and create Project instances. '''
    # title formats
    ADD_FORMAT     = 'Adding to {!r}'
    EDIT_FORMAT    = 'Editing {!r}'
    # mode button text
    GOTO_ADD_MODE  = '++'
    GOTO_EDIT_MODE = '\u21e6'

    def __init__(self, master, bindings, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master
        self._bindings = bindings

        self._create_display()

    def _create_display(self):
        ''' '''
        self._create_title()
        self._create_fields()
        self._create_buttons()

    def _create_title(self):
        ''' '''
        title_frame = tk.Frame(self)
        title_frame.grid(columnspan=2)
        self._title = FormattedStringVar()
        self._title_label = tk.Label(title_frame, textvariable=self._title,
                                     font=HEADING_FONT)
        self._title_entry = tk.Entry(title_frame) # TODO grid when editing title

        self._title_label.grid(row=0)

    def _create_fields(self):
        ''' '''
        self._entries = {}
        for index, value in enumerate(['name', 'details', 'sub_projects',
                                       'due_date', 'precursors', 'duration',
                                       'scheduled_time', 'completion_date']):
            text = value.replace('_', ' ')
            self._entries[value] = \
                    LabelEntry(self, dict(text=text, anchor='e'), row=index+1)
            self._entries[value].bind(CTRL('Return'),
                                      self._bindings[SUBMIT_BIND])
            self._entries[value].bind(CTRL('BackSpace'),
                                      self._bindings[DELETE_BIND])

    def _create_buttons(self):
        ''' '''
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
        ''' '''
        submission_results = {}
        for name in self._entries:
            entry = self._entries[name]
            result = entry.get()
            if result:
                submission_results[name.replace(' ','_')] = result
            entry.clear()
        return submission_results

    def display_selection_data(self, data):
        ''' '''
        for name in data:
            self._entries[name].set(data[name])

    def set_edit_mode(self, new_project=None):
        ''' '''
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
        ''' '''
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
        self._clear()
        # update buttons
        self._add_mode_button.config(text=self.GOTO_EDIT_MODE)
        self._submit_button.grid()
        self._delete_button.grid_remove()

    def _clear(self):
        ''' '''
        for entry in self._entries.values():
            entry.clear()


class ProjectsDisplay(tk.Frame):
    ''' A display element for a collection of ProjectViews. '''
    def __init__(self, master, projects, bindings, title=None,
                 show_complete=True, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master
        self._bindings = bindings
        self._show_complete = show_complete

        if title:
            self._title = tk.Label(self, text=title, font=HEADING_FONT)
            self._title.grid(sticky='ew')

        self.bind('<Button-1>', self._bindings[RESTORE_BIND])

        self._projects = []
        self._project_views = []
        for project in projects:
            self.add_project(project)

        # TODO scrollbars

    def add_project(self, project):
        ''' Add a Project to the display. '''
        self._projects.append(project)
        project_view = ProjectView(self, project, bindings=self._bindings,
                                   show_complete=self._show_complete)
        self.add_project_view(project_view)

    def add_project_view(self, project_view, project=None):
        ''' Add a ProjectView to the display. '''
        if project:
            self._projects.append(project)
        if not project_view.hidden:
            project_view.grid(sticky=tk.W+tk.E)
        self._project_views.append(project_view)

    def remove_project(self, project):
        ''' Remove and return a ProjectView from the display. '''
        for project_view in self._project_views:
            if project_view._project is project:
                project_view.grid_remove()
                return self._project_views.remove(project_view)


class MainView(tk.Frame):
    ''' '''
    # modification modes
    ADD_MODE  = 'add'
    EDIT_MODE = 'edit'
    MOVE_MODE = 'move'

    def __init__(self, master, main_project, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master
        self._main_project = main_project

        # pre-sorting of projects
        self._planned = []
        self._unordered = []
        self._sort_projects()

        # creation
        display = dict(bd=1, relief=tk.RAISED)
        display_bindings = {
            FOCUS_BIND: self._focus_binding,
            RESTORE_BIND: self._restore_binding,
        }
        editor_bindings = {
            ADD_BIND: self._add_binding,
            SUBMIT_BIND: self._submit_binding,
            DELETE_BIND: self._delete_binding,
        }
        self._planned_display = ProjectsDisplay(self, self._planned,
                display_bindings, 'planned to do', **display)
        self._unordered_display = ProjectsDisplay(self, self._unordered,
                display_bindings, 'to do', **display)
        self._project_editor = ProjectEditor(self, editor_bindings, **display)

        # layout
        self._planned_display.grid(row=0, column=0, rowspan=2, sticky='news')
        self._unordered_display.grid(row=0, column=1, sticky='news')
        self._project_editor.grid(row=1, column=1, sticky='news')

        # post setup
        self._focus_project = None
        self._set_focus(self._main_project)
        self.bind('<Escape>', lambda e: self._set_focus(self._main_project))

    def _sort_projects(self):
        ''' Sort the projects in MAIN_NAME into 'planned' and 'unordered'. '''
        for name in self._main_project.sub_projects:
            project = self._main_project.sub_projects[name]
            if self._project_planned(project):
                self._planned.append(project)
            else:
                self._unordered.append(project)

    @staticmethod
    def _project_planned(project):
        ''' Returns True if 'project' is classified as planned. '''
        # currently based on just if a project has sub-projects
        return bool(project.sub_projects)

    def _set_focus(self, project, mode=None):
        ''' Set focus on the specified project in 'mode' or edit mode. '''
        if project == self._focus_project and \
           (mode is None or mode == self._mode):
            project = self._main_project # restore focus to main project

        self._focus_project = project
        # TODO handle project_editor display
        if self._focus_project == self._main_project:
            self._mode = self.ADD_MODE
        else:
            self._mode = mode or self.EDIT_MODE

        if self._mode == self.EDIT_MODE:
            self._project_editor.set_edit_mode(project)
        elif self._mode == self.ADD_MODE:
            self._project_editor.set_add_mode(project.name)
        # else MOVE_MODE, so no need to update editor

    def _focus_binding(self, project):
        ''' '''
        self._set_focus(project, mode=self.EDIT_MODE)

    def _restore_binding(self, event=None):
        ''' '''
        self._set_focus(self._main_project)

    def _add_binding(self, event=None):
        ''' '''
        if self._mode == self.ADD_MODE:
            mode = self.EDIT_MODE
        else:
            mode = self.ADD_MODE

        self._set_focus(self._focus_project, mode)

    def _submit_binding(self, event=None):
        ''' '''
        # TODO update for adding to not main, and editing
        already_planned = self._project_planned(self._focus_project)

        # create a new project from the submission
        new_proj = self._focus_project.create_sub_project(
                **self._project_editor.get_submission_results())
        self._focus_project.save()

        if not already_planned and \
           self._project_planned(self._focus_project):
            # planned now, so move appropriately
            self._planned_display.add_project_view(
                    project_view=self._unordered_display.remove_project(
                    self._focus_project), project=self._focus_project)
        elif self._focus_project == self._main_project:
            if self._project_planned(new_proj):
                self._planned.append(new_proj)
                self._planned_display.add_project(new_proj)
            else:
                self._unordered.append(new_proj)
                self._unordered_display.add_project(new_proj)

    def _delete_binding(self, event=None):
        ''' '''
        removee = self._focus_project
        parent = removee._parent

        if not parent:
            return # don't try to delete main

        if parent == self._main_project:
            # remove from planned/unordered
            if self._project_planned(removee):
                self._planned.remove(removee)
                self._planned_display.remove_project(removee)
            else:
                self._unordered.remove(removee)
                self._unordered_display.remove_project(removee)
        # else: display removal handled by ProjectView

        parent.remove_sub_project(removee)
        parent.save()
        # set focus back to main project
        # TODO perhaps change this to next project down, or to parent?
        self._set_focus(self._main_project)
