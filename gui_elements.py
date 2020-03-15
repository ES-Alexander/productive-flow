#!/usr/bin/env python3

from low_level_elements import * # tk, LabelEntry, FormattedStringVar

from sys import platform
if platform.startswith('darwin'):
    CLICK_CURSOR = 'pointinghand'
else:
    CLICK_CURSOR = 'double_arrow'

HEADING_FONT = ('Helvetica', 16, 'bold')

class ProjectView(tk.Frame):
    ''' The basic display of a project. '''
    def __init__(self, master, project, focus_binding, default_show=True,
                 show_complete=True, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master
        self._project = project
        self._focus_binding = focus_binding

        self._name = tk.Label(self, text=self._project.name, anchor=tk.W)
        self._name.grid(row=0, column=1, sticky='w')
        self._name.bind('<Button-1>',
                        lambda event: self._focus_binding(self._project))
        self._the_og_bg = self._name.cget('background')

        self._show_complete = show_complete
        self.hidden = False

        self._init = True
        if self._project.complete:
            self.update_name_complete()
        else:
            self.update_name_not_complete()
        self._init = False

        # TODO due date display

        if self._project.sub_projects:
            self._sub_projects = ProjectsDisplay(self,
                    self._project.sub_projects.values(), self._focus_binding,
                    show_complete=self._show_complete)
            self._minimise = tk.Label(self, cursor=CLICK_CURSOR)
            self._minimise.grid(row=0, column=0, sticky='n')
            self.maximise()
            if not default_show:
                self.minimise()
        else:
            self._spacer = tk.Label(self, text=' '*2)
            self._spacer.grid(row=0, column=0)

    def update_name_complete(self):
        if self._show_complete:
            self._name.config(bg='green')
            self._name.bind('<Double-Button-1>', self.remove_complete)
        else:
            self.hidden = True
            if not self._init:
                self.grid_remove()

    def _save_update(self):
        ''' Saves the stored project and refreshes its focus. '''
        self._project.save()
        # toggle focus off then back on refreshed
        for toggle in range(2):
            self._focus_binding(self._project)

    def complete(self, event=None):
        ''' Binding for completion of the Project. '''
        self._project.set_complete()
        self._save_update()
        self.update_name_complete()

    def update_name_not_complete(self):
        ''' '''
        self._name.config(bg=self._the_og_bg)
        self._name.bind('<Double-Button-1>', self.complete)

    def remove_complete(self, event=None):
        ''' Remove complete status from Project. '''
        self._project.complete = False
        self._project.completion_date = None
        self._save_update()
        self.update_name_not_complete()

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
    ADD_FORMAT  = 'Adding to {!r} Project'
    EDIT_FORMAT = 'Editing {!r} Project'

    def __init__(self, master, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master

        self._initialise_bindings()

        self._create_display()

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

    def set_edit_mode(self, data):
        ''' '''
        self._title.set_format_string(self.EDIT_FORMAT)
        self._title.set(data['name'])
        self.display_selection_data(data)

    def set_add_mode(self, name):
        ''' '''
        self._title.set_format_string(self.ADD_FORMAT)
        self._title.set(name)
        self._clear()

    def _clear(self):
        ''' '''
        for entry in self._entries.values():
            entry.clear()

    def _initialise_bindings(self):
        ''' '''
        self._bindings = {
            'submit': lambda *args, **kwargs: None,
            'delete': lambda *args, **kwargs: None,
        }

    def _create_display(self):
        ''' '''
        self._create_title()
        self._create_entries()
        self._create_buttons()

    def _create_title(self):
        ''' '''
        self._title = FormattedStringVar()
        tk.Label(self, textvariable=self._title, font=HEADING_FONT).grid(
                columnspan=2)

    def _create_entries(self):
        ''' '''
        self._entries = {}
        for index, value in enumerate(['name', 'sub_projects','details',
                                       'due_date', 'precursors', 'duration',
                                       'scheduled_time', 'completion_date']):
            text = value.replace('_', ' ')
            self._entries[value] = LabelEntry(self,
                                              dict(text=text, anchor='e'),
                                              row=index+1)
        self._button_row = index+2

    def _create_buttons(self):
        ''' '''
        self._submit_button = tk.Button(self, text='submit',
                                        command=self._submit_binding)
        self._submit_button.grid(row=self._button_row, column=1, sticky='news')

    def _submit_binding(self, event=None):
        ''' '''
        self._bindings['submit'](event)

    def set_binding(self, name, func):
        ''' Sets 'func' as the binding accessed by 'name'. '''
        self._bindings[name] = func

class ProjectsDisplay(tk.Frame):
    ''' A display element for a collection of ProjectViews. '''
    def __init__(self, master, projects, focus_binding, title=None,
                 show_complete=True, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master
        self._focus_binding = focus_binding
        self._show_complete = show_complete

        if title:
            self._title = tk.Label(self, text=title, font=HEADING_FONT)
            self._title.grid(sticky='ew')

        self._projects = []
        self._project_views = []
        for project in projects:
            self.add_project(project)

        # TODO scrollbar

    def add_project(self, project):
        ''' Add a Project to the display. '''
        self._projects.append(project)
        project_view = ProjectView(self, project,
                                   show_complete=self._show_complete,
                                   focus_binding=self._focus_binding)
        self.add_project_view(project_view)

    def add_project_view(self, project_view, project=None):
        ''' Add a ProjectView to the display. '''
        if project:
            self._projects.append(project)
        if not project_view.hidden:
            project_view.grid(sticky=tk.W+tk.E)
        self._project_views.append(project_view)

    def remove_project(self, project):
        ''' Remove and return a ProejctView from the display. '''
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
        self._planned_display = ProjectsDisplay(self, self._planned,
                self.focus_binding, 'planned to do', **display)
        self._unordered_display = ProjectsDisplay(self, self._unordered,
                self.focus_binding, 'to do', **display)
        self._project_editor = ProjectEditor(self, **display)

        # layout
        self._planned_display.grid(row=0, column=0, rowspan=2, sticky='news')
        self._unordered_display.grid(row=0, column=1, sticky='news')
        self._project_editor.grid(row=1, column=1, sticky='news')

        # connection
        self._set_bindings()

        # post setup
        self._focus_project = None
        self._set_focus(self._main_project)

    def _sort_projects(self):
        ''' '''
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
        ''' '''
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
            self._project_editor.set_edit_mode(project.get_properties())
        elif self._mode == self.ADD_MODE:
            self._project_editor.set_add_mode(project.name)
        # else MOVE_MODE, so no need to update editor

    def _set_bindings(self):
        ''' '''
        self._set_submit_binding()
        self._set_delete_binding()
        #self._set_focus_binding()

    def focus_binding(self, project):
        self._set_focus(project, mode=self.EDIT_MODE)

    """
    def _set_focus_binding(self):
        ''' '''
        def focus_binding(project):
            ''' '''
            self._set_focus(project, mode=self.EDIT_MODE)

        self._planned_display.set_focus_binding(focus_binding)
        self._unordered_display.set_focus_binding(focus_binding)
    """

    def _set_delete_binding(self):
        ''' '''
        def delete_binding(event=None):
            ''' '''
            removee = self._focus_project
            parent = removee._parent
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

        self._project_editor.set_binding('delete', delete_binding)

    def _set_submit_binding(self):
        ''' '''
        def submit_binding(event=None):
            ''' '''
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
                    self._planned_display.add_project(new_proj)
                else:
                    self._unordered_display.add_project(new_proj)

        self._project_editor.set_binding('submit', submit_binding)


