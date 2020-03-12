#!/usr/bin/env python3

from project import Project

main = Project('main')

"""
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
"""

print('Enter item names, with optional elaboration.',
      "To quit, enter a single 'q' as the name of the next item.",
      'To elaborate, enter parameters and values in the form:',
      'param = value,',
      'making sure to denote values with appropriate Python syntax',
      "(e.g. my_str = 'String',).\n",
      'Elaboration options include:',
      "details = '''Your detail string'''",
      "To finish elaborating, press enter on a blank line.", sep='\n')

while True:
    name = input('Next item: ')
    if not name:
        break
    info = ''
    elaboration = input('parameters?')
    while elaboration:
        info += elaboration
        elaboration = input()

    main.create_sub_project(name, **eval('dict({})'.format(info)))

if input('Save state? [y/n]: ').lower() != 'n':
    main.save()
