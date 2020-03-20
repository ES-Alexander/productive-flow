#!/usr/bin/env python3

from project import Project
from gui_elements import *

class MainView(ProjectViewBase):
    ''' The main view element, initialising and containing all others. '''
    # modification modes
    ADD_MODE  = 'add'
    EDIT_MODE = 'edit'
    MOVE_MODE = 'move'

    def __init__(self, master, main_project, **kwargs):
        ''' Create and set up the view elements. '''
        super().__init__(master, main_project, **kwargs)
        self._root_project = self._project

        self._create_display()

    def _create_display(self):
        ''' Create the main display elements. '''
        # relevant inputs
        planned, unordered = self._sort_projects()
        display = dict(bd=1, relief=tk.RAISED)
        display_bindings, editor_bindings = self._get_bindings()

        # object creation
        self._planned_display = ProjectsDisplay(self, planned,
                display_bindings, 'planned to do', **display)
        self._unordered_display = ProjectsDisplay(self, unordered,
                display_bindings, 'to do', **display)
        self._project_editor = ProjectEditor(self, editor_bindings, **display)

        # layout
        self._planned_display.grid(row=0, column=0, rowspan=2, sticky='news')
        self._unordered_display.grid(row=0, column=1, sticky='news')
        self._project_editor.grid(row=1, column=1, sticky='news')

        # post setup
        self._focus_view = self
        self._set_focus(self)
        self.bind('<Escape>', lambda e: self._set_focus(self))

    def _sort_projects(self):
        ''' Sort this view's projects into 'planned' and 'unordered'. '''
        planned = []; unordered = [] # initialise sort lists
        for project in self._project.sub_projects.values():
            if self._project_planned(project):
                planned.append(project)
            else:
                unordered.append(project)

        return planned, unordered

    def _project_planned(self, project):
        ''' Returns True if 'project' is classified as planned.

        Currently based solely on if 'project' has sub-projects.

        'project' is a direct sub-project of this view's internal project.

        '''
        return bool(project.sub_projects)

    def _get_bindings(self):
        ''' Return the bindings for ProjectDisplays and a ProjectEditor. '''
        display_bindings = {
            FOCUS_BIND: self._focus_binding,
            RESTORE_BIND: self._restore_binding,
        }
        editor_bindings = {
            ADD_BIND: self._add_binding,
            SUBMIT_BIND: self._submit_binding,
            DELETE_BIND: self._delete_binding,
        }

        return display_bindings, editor_bindings


    def _set_focus(self, view, mode=None):
        ''' Set focus on the specified project in 'mode' or edit mode. '''
        if self._focus_view is not self:
            self._focus_view._toggle_focus() # must be a ProjectView

        if (view is self and self._project is self._root_project) or \
           (view is self._focus_view and (mode is None or mode == self._mode)):
            # root project (only has add mode), or restoring 
            # or restoring
            self._mode = self.ADD_MODE
        else:
            self._mode = mode or self.EDIT_MODE

        project = view._project
        self._focus_view = view
        if self._focus_view is not self:
            self._focus_view._toggle_focus()

        if self._mode == self.EDIT_MODE:
            self._project_editor.set_edit_mode(project)
        elif self._mode == self.ADD_MODE:
            self._project_editor.set_add_mode(project.name)
        # else MOVE_MODE, so no need to update editor

    def _focus_binding(self, project_view):
        ''' The binding used to set focus to a given project. '''
        self._set_focus(project_view, mode=self.EDIT_MODE)

    def _restore_binding(self, event=None):
        ''' The binding used to restore focus to the main project. '''
        self._set_focus(self)

    def _add_binding(self, event=None):
        ''' The binding used by the editor add/edit mode switcher. '''
        if self._mode == self.ADD_MODE:
            mode = self.EDIT_MODE
        else:
            mode = self.ADD_MODE

        self._set_focus(self._focus_view, mode)

    def _submit_binding(self, event=None):
        ''' The binding used to submit the editor data-field values. '''
        # TODO update for editing
        if self._mode == self.ADD_MODE:
            focus_project = self._focus_view._project
            general_project = focus_project in \
                    self._project.sub_projects.values()
            if general_project:
                already_planned = self._project_planned(focus_project)

            # create a new project from the submission
            new_project = self._focus_view.create_sub_project(
                    **self._project_editor.get_submission_results())

            if general_project:
                if not already_planned and \
                   self._project_planned(focus_project):
                    # planned now, so move appropriately
                    self._planned_display.add_project_view(
                            project_view=self._unordered_display.remove_project(
                            focus_project), project=focus_project)
                elif self._focus_view is self:
                    if self._project_planned(new_proj):
                        self._planned.append(new_proj)
                        self._planned_display.add_project(new_proj)
                    else:
                        self._unordered.append(new_proj)
                        self._unordered_display.add_project(new_proj)
            else:
                # not a direct sub-project of main, just create a project view
                self._focus_view.add_project(new_proj)
        else: # mode == self.EDIT_MODE
            self._focus_view.update_project(
                    **self._project_editor.get_submission_results())


    def _delete_binding(self, event=None):
        ''' The binding used to delete the in-focus ProjectView. '''
        removee = self._focus_view
        parent = removee._parent

        if not isinstance(parent, ProjectsDisplay):
            return # don't try to delete main

        if parent == self:
            # remove from planned/unordered
            if self._project_planned(removee._project):
                self._planned.remove(removee)
                self._planned_display.remove_project(removee)
            else:
                self._unordered.remove(removee)
                self._unordered_display.remove_project(removee)
        # else: display removal handled by ProjectView

        parent.remove_sub_project(removee)
        parent.save()
        # set focus back to main parent of deleted project
        self._set_focus(parent)


class Controller(object):
    ''' The controller, to load the project and initialise and run the GUI. '''
    def __init__(self, **kwargs):
        ''' Creates a Tk window with a MainView display of the Project. '''
        self._root = tk.Tk()
        self._project = Project(MAIN_NAME)
        self._view = MainView(self._root, self._project, **kwargs)
        self._view.grid(sticky='nsew')

        self._root.mainloop()


if __name__ == '__main__':
    Controller()
