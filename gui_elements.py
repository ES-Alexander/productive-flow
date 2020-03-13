#!/usr/bin/env python3

from low_level_elements import * # tk, LabelEntry, FormattedStringVar

HEADING_FONT = ('Helvetica', 16, 'bold')

class ProjectView(tk.Frame):
    ''' The basic display of a project. '''
    def __init__(self, master, project, show_sub_projects=True, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master
        self._project = project

        self._name = tk.Label(self, text=self._project.name, anchor=tk.W)
        self._name.grid(columnspan=2)

        if self._project.complete:
            self.config(bg='green')
        # TODO completion checkbox
        # TODO due date display

        if show_sub_projects and self._project.sub_projects:
            self._sub_projects = ProjectsDisplay(self,
                    self._project.sub_projects.values())
            self._sub_projects.grid(column=1)

class DetailedProjectView(ProjectView):
    ''' The detailed display of a project. '''
    def __init__(self, master, project, **kwargs):
        ''' '''
        super().__init__(master, project, **kwargs)
        # TODO

class ProjectEditor(tk.Frame):
    ''' A widget to create a project '''
    def __init__(self, master, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master

        self._initialise_bindings()

        self._create_display()

    def _initialise_bindings(self):
        ''' '''
        self._bindings = {
            'submit': lambda *args, **kwargs: None,
        }

    def _create_display(self):
        ''' '''
        self._create_title()
        self._create_entries()
        self._create_buttons()

    def _create_title(self):
        ''' '''
        self._title = FormattedStringVar(format_str='Add to {}')
        tk.Label(self, textvariable=self._title, font=HEADING_FONT).grid(
                columnspan=2)
        self._title.set("unordered")

    def _create_entries(self):
        ''' '''
        self._entries = {}
        for index, value in enumerate(['name', 'details', 'due_date',
                                       'completion_date']):
            text = value.replace('_', ' ')
            self._entries[value] = LabelEntry(self,
                                              dict(text=text, anchor='e'),
                                              row=index+1)

    def _create_buttons(self):
        ''' '''
        self._submit_button = tk.Button(self, text='submit',
                                        command=self._bindings['submit'])
        self._submit_button.grid(column=1, sticky='news')

    def set_binding(self, name, func):
        ''' Sets 'func' as the binding accessed by 'name'. '''
        self._bindings[name] = func

class ProjectsDisplay(tk.Frame):
    ''' A display element for a collection of ProjectViews. '''
    def __init__(self, master, projects, title=None, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master

        if title:
            self._title = tk.Label(self, text=title, font=HEADING_FONT)
            self._title.grid()

        if not projects:
            projects = []
        self._create_project_views(projects)

        # TODO scrollbar

    def _create_project_views(self, projects):
        ''' '''
        self._project_views = []
        for project in projects:
            self._add_project(project)

    def _add_project(self, project):
        ''' Add a Project to the display. '''
        project_view = ProjectView(self, project)
        project_view.grid(sticky=tk.W+tk.E)
        self._project_views.append(project_view)

    def _remove_project(self, project):
        ''' Remove and return a ProejctView from the display. '''
        for project_view in self._project_views:
            if project_view._project is project:
                project_view.grid_remove()
                return self._project_views.remove(project_view)

class MainView(tk.Frame):
    ''' '''
    def __init__(self, master, main_project, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master
        self._main_project = main_project

        planned_projects = []
        unordered_projects = []
        for name in self._main_project.sub_projects:
            project = self._main_project.sub_projects[name]
            if project.sub_projects:
                planned_projects.append(project)
            else:
                unordered_projects.append(project)

        # creation
        self._planned_display = ProjectsDisplay(self, planned_projects,
                                                'planned/sorted', bd=5)
        self._unordered_display = ProjectsDisplay(self, unordered_projects,
                                                  'unordered', bd=5)
        self._project_editor = ProjectEditor(self, bd=5)

        # layout
        self._planned_display.grid(row=0, column=0, rowspan=2, sticky='news')
        self._unordered_display.grid(row=0, column=1, sticky='news')
        self._project_editor.grid(row=1, column=1, sticky='news')

    def connect_stuff(self, **things_funcs):
        ''' Called externally '''
        pass


