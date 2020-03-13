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
        self._name.grid(column=0, columnspan=2, sticky='ew')

        if self._project.complete:
            self._name.config(bg='green')
        # TODO completion checkbox
        # TODO due date display

        if show_sub_projects and self._project.sub_projects:
            self._sub_projects = ProjectsDisplay(self,
                    self._project.sub_projects.values())
            tk.Label(self, text=' ').grid()
            self._sub_projects.grid(row=1, column=1)

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

    def get_submission_results(self):
        ''' '''
        submission_results = {}
        for name in self._entries:
            entry = self._entries[name]
            result = entry.get()
            if result:
                submission_results[name.replace(' ','_')] = result
            entry.delete(0, tk.END)
        return submission_results

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
        self._title = FormattedStringVar(format_str='Add to {!r}')
        tk.Label(self, textvariable=self._title, font=HEADING_FONT).grid(
                columnspan=2)
        self._title.set("to do")

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
                                        command=self._submit_binding)
        self._submit_button.grid(column=1, sticky='news')

    def _submit_binding(self, event=None):
        ''' '''
        self._bindings['submit'](event)

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

        self._projects = []
        self._project_views = []
        for project in projects:
            self.add_project(project)

        # TODO scrollbar

    def add_project(self, project):
        ''' Add a Project to the display. '''
        self._projects.append(project)
        project_view = ProjectView(self, project)
        self.add_project_view(project_view)

    def add_project_view(self, project_view, project=None):
        ''' Add a ProjectView to the display. '''
        if project:
            self._projects.append(project)
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
    def __init__(self, master, main_project, **kwargs):
        ''' '''
        super().__init__(master, **kwargs)
        self._master = master
        self._main_project = main_project
        self._focus_project = self._main_project # project currently in focus

        # pre-sorting of projects
        self._planned = []
        self._unordered = []
        self._sort_projects()

        # creation
        display = dict(bd=1, relief=tk.RAISED)
        self._planned_display = ProjectsDisplay(self, self._planned,
                                                'planned to do', **display)
        self._unordered_display = ProjectsDisplay(self, self._unordered,
                                                  'to do', **display)
        self._project_editor = ProjectEditor(self, **display)

        # layout
        self._planned_display.grid(row=0, column=0, rowspan=2, sticky='news')
        self._unordered_display.grid(row=0, column=1, sticky='news')
        self._project_editor.grid(row=1, column=1, sticky='news')

        # connection
        self.set_submit_binding()

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
        return bool(project.sub_projects)

    def set_submit_binding(self):
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


