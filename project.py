#!/usr/bin/env python3

import os, shutil
from datetime import datetime, timedelta


class Project(object):
    ''' A class for storing project information, big and small. '''
    TAB = ' ' * 2
    TIME_FORMAT = '%d/%b/%Y - %H:%M' # 'dd/Mmm/yyyy - hh:mm'

    def __init__(self, name, path='projects', **kwargs):
        ''' Initialise a project.

        'name' must be a unique string in the project tree.
        'path' is absolute, or relative to the script running location.
        **kwargs options:
            'details' is a string specifying notes or details about the
                Project.
            'sub_projects'* is a list of Project instances which are
                sub-projects of this Project, or a list of their names.
            'due_date' is a datetime instance of when this Project is due, or
                a string with format Project.TIME_FORMAT.
            'completion_date' is the true or desired completion date, depending
                on if 'complete' is True or False, as a datetime or a string in
                Project.TIME_FORMAT format.
            'duration' is the true or expected duration depending on
                'complete', as a string in form 'xd' or 'xh' for days/hours
                respectively, or as a timedelta object.
            'scheduled_time' is the amount of time scheduled for this Project
                as a string in form 'xd' or 'xh' for days/hours respectively,
                or as a timedelta object.
            'precursors'* is a list of Project instances which must be
                completed before this one can be started, or a list of their
                names.
            'parent' is the parent of self, if it exists and is initialised.

            * these lists can also contain a mixture of initialised Project
                instances, and Project names.

        '''
        if not os.path.isdir(path):
            os.makedirs(path) # create target and intermediate directories

        self.name              = name
        self._save_file        = path + '/{}.txt'.format(self.name)
        self._modified         = True # assume this is new/a modification

        if os.path.isfile(self._save_file):
            # this Project has previously been saved
            if not any([x in kwargs for x in \
                        ['details', 'sub_projects', 'due_date',
                         'completion_date', 'complete', 'duration',
                         'scheduled_time', 'precursors']]):
                # initialise from saved file
                with open(self._save_file) as info:
                    # insertion security risk - does it matter?
                    kwargs.update(eval('dict({})'.format(info.read())))
                self._modified = False

        self.details           = kwargs.get('details', '')
        self.path              = path
        self._sub_project_path = path + '/' + name

        self.complete = kwargs.get('complete', False)
        self.set_due_date(kwargs.get('due_date', None))
        self.set_completion_date(kwargs.get('completion_date', None))
        self.set_duration_estimate(kwargs.get('duration', None))
        self.update_scheduled_time(kwargs.get('scheduled_time', None))

        self._parent    = kwargs.get('parent', None)
        if self._parent:
            self._level = self._parent._level + 1
        else:
            self._level = 0

        # must occur after self._parent and paths initialised
        self.sub_projects = {}
        self._load_sub_projects(kwargs.get('sub_projects', []))
        self.precursors   = {}
        self._load_precursors(kwargs.get('precursors', []))

        if self._modified:
            self.save()

    def __modifier(func):
        ''' A wrapper for functions which modify the internal state. '''
        def func_wrapper(self, *args, **kwargs):
            self._modified = True
            return func(self, *args, **kwargs)
        return func_wrapper

    def _load_sub_projects(self, sub_projects):
        ''' '''
        names = []
        for sub_project in sub_projects:
            if isinstance(sub_project, str):
                names.append(sub_project) # add in creation loop below
            else:
                # assume as valid Project, with appropriate connections
                self.add_sub_project(sub_project, modifier=False)

        for name in names:
            # allow for sub_projects to have been added as precursors to
            #   earlier sub_projects
            if name not in self.sub_projects:
                self.create_sub_project(name)

    def _load_precursors(self, precursors):
        ''' '''
        names = []
        for precursor in precursors:
            if isinstance(precursor, str):
                names.append(precursor) # add in creation loop below
            else:
                # assume as valid Project, with appropriate connections
                self.add_precursor(precursor, modifier=False)

        if self._parent:
            for name in names:
                if name in self._parent.precursors:
                    self.add_precursor(self._parent.precursors[name],
                                       modifier=False)
                else:
                    precursor = self.create_precursor(name)
                    self._parent.add_sub_project(precursor)
        else:
            for name in names:
                self.create_precursor(name)


    @__modifier
    def rename(self, name):
        ''' '''
        if self._level == 0:
            raise Exception('Cannot rename a Project with no '
                            'instantiated parent')
        old_name = self.name
        self.name = name
        self.replace_files(old_name, name)
        self._parent._sub_project_renamed(old_name, new_name)

    def _replace_files(self, old_name, new_name):
        ''' '''
        old_dir = self.path + '/{}/'.format(old_name)
        new_dir = self.path + '/{}/'.format(new_name)
        if os.path.isfile(self._save_file):
            old_save = self._save_file
            self._save_file = new_dir[:-1] + '.txt'
            os.rename(old_save, self._save_file)
        if os.path.isdir(old_dir):
            os.rename(old_dir, new_dir)

    @__modifier
    def _sub_project_renamed(self, old_name, new_name):
        ''' '''
        self.sub_projects[new_name] = self.sub_projects.pop(old_name)
        for name in self.sub_projects:
            sub_project = self.sub_projects[name]
            sub_project._precursor_renamed(old_name, new_name)

    @__modifier
    def _precursor_renamed(self, old_name, new_name):
        ''' Rename the precursor with old_name to new_name, if it exists. '''
        if old_name in self.precursors:
            self.precursors[new_name] = self.precursors.pop(old_name)

    @__modifier
    def update_details(self, details):
        ''' Update the details parameter of this Project. '''
        self.details = details

    @__modifier
    def set_complete(self, completion_date=None):
        ''' Set this Project as complete, now or as specified. '''
        self.complete = True
        if not completion_date:
            # assume completion was now
            completion_date = datetime.today()
        self.set_desired_completion_date(completion_date)

    @__modifier
    def set_due_date(self, due_date):
        ''' Set or reset the due date for this Project. '''
        self.due_date = self._format_datetime(due_date)

    @__modifier
    def set_completion_date(self, completion_date):
        ''' Set the completion date for this Project. '''
        self.completion_date = self._format_datetime(completion_date)

    @__modifier
    def set_duration_estimate(self, duration):
        ''' check against earliest start date from dependencies, and
            desired completion date, and scheduled time
        '''
        self.duration = self._format_duration(duration)

    @__modifier
    def update_scheduled_time(self, amount):
        ''' Check against durations estimate '''
        self.scheduled_time = self._format_duration(amount)

    def add_sub_project(self, sub_project, modifier=True):
        ''' Add the specified Project as a sub-project to this project.

        'modifier' specifies whether this method is being used as a modifier
            (external adding of a sub_project) or automatically on
            initialisation.

        '''
        if modifier or sub_project._modified:
            self._modified = True
        self.sub_projects[sub_project.name] = sub_project
        return sub_project

    def create_sub_project(self, name, **kwargs):
        ''' Create a new sub-project Project with given parameters. '''
        sub_project_file = self._sub_project_path + '/{}.txt'.format(name)
        return self.add_sub_project(modifier=os.path.isfile(sub_project_file),
                sub_project=Project(name, path=self._sub_project_path,
                                    parent=self, **kwargs))

    @__modifier
    def remove_sub_project(self, sub_project):
        ''' Remove the specified Project from this Project's sub-projects.

        Also removes the Project as a precursor to other projects, and deletes
            any files and directories belonging to the Project.

        Raises an KeyError if sub_project is not a sub-project of self.

        '''
        name = sub_project.name
        self.sub_projects.pop(name)
        for sub_project in self.sub_projects.values():
            sub_project.precursors.pop(name, None)
        sub_project_dir = self._sub_project_path + '/{}/'.format(name)
        sub_project_file = sub_project_dir[:-1] + '.txt'
        if os.path.isfile(sub_project_file):
            os.remove(sub_project_file)
        if os.path.isdir(sub_project_dir):
            shutil.rmtree(sub_project_dir)

    def add_precursor(self, precursor, modifier=True):
        ''' Flag the specified Project as a precursor to self.

        'precursor' is a Project instance which must be completed before self
            can be started.
        'modifier' specifies whether this method is being used as a modifier
            (external adding of a precursor) or automatically on
            initialisation.

        '''
        if modifier:
            self._modified = True

        self.precursors[precursor.name] = precursor
        return precursor

    def create_precursor(self, name, **kwargs):
        ''' '''
        # TODO check the logic of when to set modifier to True
        precursor_file = self._path + '/{}.txt'.format(name)
        return self.add_precursor(Project(name, path=self.path,
                                          parent=self._parent, **kwargs),
                                  modifier=os.path.isfile(precursor_file))

    @__modifier
    def remove_precursor(self, name):
        ''' '''
        try:
            self.precursors.pop(name)
        except KeyError:
            print('{} is not a known precursor of {}.'.format(name, self.name))

    def save(self, force=True):
        ''' Save the state of this Project and its sub_projects. '''
        if self._modified or force:
            save_out = self._gen_save_string()
            with open(self._save_file, 'w') as save_file:
                save_file.write(save_out)

        for sub_project in self.sub_projects.values():
            sub_project.save()

    def _gen_save_string(self):
        ''' Generate a string version of self to save to file. '''
        save_str = ''
        if self.details:
            save_str += 'details = """{}""",\n'.format(self.details)
        if self.sub_projects:
            save_str += 'sub_projects = ["{}"],\n'.format(
                    '","'.join(self.sub_projects.keys()))
        if self.due_date:
            save_str += 'due_date = "{}",\n'.format(datetime.strftime(
                    self.due_date, self.TIME_FORMAT))
        if self.completion_date:
            save_str += 'completion_date = "{}",\n'.format(datetime.strftime(
                    self.completion_date, self.TIME_FORMAT))
        if self.complete:
            save_str += 'complete = True,\n'
        if self.duration:
            save_str += 'duration = "{}h",\n'.format(
                    self.duration / timedelta(hours=1))
        if self.scheduled_time:
            save_str += 'scheduled_time = "{}h",\n'.format(
                    self.scheduled_time / timedelta(hours=1))
        if self.precursors:
            save_str += 'precursors = ["{}"],\n'.format(
                    '","'.join(self.precursors.keys()))
        return save_str

    @classmethod
    def _format_datetime(cls, date):
        ''' Format the inputted date as a datetime instance. '''
        if isinstance(date, datetime):
            return date
        if isinstance(date, str):
            return datetime.strptime(date, cls.TIME_FORMAT)

    @staticmethod
    def _format_duration(duration):
        ''' Format the inputted duration as a timedelta instance. '''
        if isinstance(duration, timedelta):
            return duration
        if isinstance(duration, str):
            if 'h' in duration:
                return timedelta(hours=float(duration[:-1]))
            return timedelta(days=float(duration[:-1]))

    def print(self):
        ''' Custom print to handle printing from low levels, and add a
            trailing newline.
        '''
        out = str(self)
        if not '\n' in out:
            print(out)
            return

        # handle potential excess indent if not printing from level 0
        out = out.split('\n')
        offset = -len(self.TAB)
        for char in out[1]:
            if char == ' ':
                offset += 1
            else:
                break
        print(out[0] + '\n' + \
               '\n'.join([line[offset:] for line in out[1:]]) + '\n')

    def __str__(self):
        ''' '''
        # TODO update with complete, completion date, duration, scheduled time
        ret_val = 'Project({}'.format(self.name)
        if self.due_date:
            ret_val += ', due:{}'.format(datetime.strftime(self.due_date,
                                                           self.TIME_FORMAT))
        ret_val += ')'
        prefix = (self._level + 1) * self.TAB
        if self.details:
            ret_val += '\n' + prefix
            detail_string = '{!r}'.format(self.details)
            if '\n' in detail_string:
                ret_val += ('\n' + prefix).join(detail_string.split('\n'))
            else:
                ret_val += detail_string
        for name in self.sub_projects:
            ret_val += '\n'
            ret_val += prefix + '{!s}'.format(self.sub_projects[name])

        return ret_val

if __name__ == '__main__':
    p = Project('testing')
    p.print()
    m = p.create_sub_project('more_testing', due_date='12/Mar/2020 - 00:00')
    m.print()
    p.print()
    e = p.create_sub_project('even_more')
    p.print()
    g = e.create_sub_project('grandchild', due_date='14/Mar/2020 - 00:00',
                       details='Quite nested down here...')
    g.print()
    p.print()
    p.create_sub_project('some_more', due_date='10/Mar/2020 - 00:00')
    p.print()
    g.create_sub_project('greatgrand', due_date='13/Mar/2020 - 00:00')
    g.print()
    p.print()
    p.save()
