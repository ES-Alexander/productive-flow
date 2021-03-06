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

        # expansion
        #self.grid_rowconfigure(0, weight=1)
        #for column in range(2):
        #    self.grid_columnconfigure(column, weight=1)

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
            SCROLL_BIND: lambda event: None,
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
            self._mode = self.ADD_MODE
            if view is self._focus_view and view is not self and \
               mode == self._mode:
                view = self
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
        ''' The binding used to submit the editor data-field values.

        DOES NOT MODIFY DISPLAY FOR CHANGED PRECURSORS/SUBPROJECTS/COMPLETION

        '''
        # TODO update for editing
        submission = self._project_editor.get_submission_results()
        if self._mode == self.ADD_MODE:
            focus_project = self._focus_view._project
            # check if adding to child of main (for planned/unplanned sorting)
            is_general_project = focus_project in \
                    self._project.sub_projects.values()
            if is_general_project:
                already_planned = self._project_planned(focus_project)

            # create (and display) a new project from the submission
            self._focus_view.create_sub_project(**submission)

            # if adding to a currently unordered sub-project of main:
            if is_general_project and not already_planned:
                # planned now, so move appropriately
                project_view = self._planned_display.add_project_view(
                        self._unordered_display.remove_project_view(
                            self._focus_view))
                self._set_focus(project_view)

            self._project_editor.clear()

        else: # mode == self.EDIT_MODE
            self._focus_view.update_project(**submission)


    def _delete_binding(self, event=None):
        ''' The binding used to delete the in-focus ProjectView. '''
        removee = self._focus_view

        if removee is self:
            print("Cannot delete main project") # SHOULDN'T BE REACHABLE
            return

        parent_view = removee.parent._master
        parent_view.remove_sub_project(removee)

        if parent_view is not self and \
           parent_view.parent._master is self and \
           not hasattr(parent_view, '_sub_projects'):
            # removing only subproject of planned general project
            #   -> move to unordered
            parent_view = self._unordered_display.add_project_view(
                self._planned_display.remove_project_view(parent_view))
        # set focus back to parent of deleted project
        self._set_focus(parent_view)

    def add_sub_project(self, project):
        ''' Adds the given project to the relevant side of the display. '''
        if self._project_planned(project):
            self._planned_display.add_project(project)
        else:
            self._unordered_display.add_project(project)

    def remove_sub_project(self, project_view):
        ''' Remove and return a ProjectView from the display. '''
        super().remove_sub_project(project_view)
        # remove from planned/unordered
        if self._project_planned(project_view._project):
            return self._planned_display.remove_project_view(project_view)
        else:
            return self._unordered_display.remove_project_view(project_view)


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
