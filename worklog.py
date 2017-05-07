#! usr/bin/env python 3

# command line journal/diary
from collections import OrderedDict
import datetime
import re
import sys


from peewee import *

from constants import Constants
from menu import Menu
from utils import clear_screen


worklog_db = SqliteDatabase('worklog.db')

class Entry(Model):
    employee_name = CharField(max_length=255)
    completed_task = CharField(max_length=30)
    date_started = DateTimeField()
    date_completed = DateTimeField()
    notes = TextField()
    time_taken = IntegerField()
    time_string = CharField()

    class Meta:
        database = worklog_db

class WorkLog(Entry):
   # worklogs = []

    def __init__(self):
        '''
        iniatlise the class; connect to the database
        and create our Entry table.
        '''
        self.main_menu = OrderedDict([
            ('1', self.add_entry),
            ('2', self.view_entries),
            ('3', self.modify_entry),
            ('4', self.delete_entry),
            ('5', self.quit)
            ])

        self.find_menu = OrderedDict([
            ('1', self.find_by_employee),
            ('2', self.find_by_date),
            ('3', self.find_by_duration),
            ('4', self.find_by_lookup),
            ('5', self.worklog_run)
            ])

        worklog_db.connect()
        worklog_db.create_tables([Entry], safe=True)

    def worklog_run(self):
        '''Main Worklog Menu'''
        while True:
            Menu(self.main_menu, 'Main Menu').menu_loop()

    def add_entry(self):
        '''Add an entry'''
        worklogs = []
        work_log = {}

        work_log.update({'Employee Name': self.get_employee_name()})
        work_log.update({'Task Completed': self.get_task()})
        work_log.update({'Date Started': self.get_date_started()})
        work_log.update({'Date Completed': self.get_date_completed(work_log['Date Started'])})

        time_taken, time_str = self.get_total_time(work_log['Date Started'],
                                                   work_log['Date Completed'])

        work_log.update({'Time Taken': time_taken})
        work_log.update({'Time String': time_str})
        work_log.update({'Notes': self.get_notes()})

        worklogs.append(work_log)

        print(Constants.GREEN + '\n' + '*' * 50 + '\n')
        print(Constants.GREEN + '   Employee Name: {} | Task Completed: {}\n' \
              .format(work_log['Employee Name'], work_log['Task Completed']))
        print(Constants.GREEN + '   Notes: {}\n'.format(work_log['Notes']))
        print(Constants.GREEN + '   Date Started: {} | Time Taken: {}'
              .format(work_log['Date Started'], work_log['Time String']))

        if input(Constants.ENDC + '\n Do you want to save the following the '
                                  'entry? [Yn] ').upper() != 'N':
            self.create_entries(worklogs)
        else:
            worklogs.pop()
            input('Work log entry has not been saved!')

    def create_entries(self, worklogs):
        ''' create the submitted entry'''
        for work in worklogs:
            Entry.create(employee_name=work['Employee Name'],
                         completed_task=work['Task Completed'],
                         date_started=work['Date Started'],
                         date_completed=work['Date Completed'],
                         notes=work['Notes'],
                         time_taken=work['Time Taken'],
                         time_string=work['Time String'])
        print('\nYour work has been saved!')

    def modify_entry(self):
        '''Modify a single entry'''
        pass


    def delete_entry(self, entry):
        '''Delete an entry'''
        if input('Are you sure [Yn] ').lower() == 'y':
            entry.delete_instance()
            print("Entry deleted!")

    def view_entries(self):
        '''Search entries'''
        Menu(self.find_menu, 'Find Work Entries').menu_loop()

    def get_employee_name(self):
        '''
        gets the employee name from the user,
        must following the convention of 'first name last name'.
        Uses a re.match expression to check the entry.
        '''
        clear_screen()
        while True:
            try:
                employee_name = input('\nPlease enter your full name i.e. '
                                      'Stuart McIntosh : ')
                if re.match(r'[\w]+\s[\w]+', employee_name):
                    return employee_name
                else:
                    raise Exception('\nInvalid entry, you must enter a name '
                                    'i.e. Stuart McIntosh')
            except Exception as error:
                print(error)
            except ValueError:
                print('Invalid entry, try again!')

    def get_task(self):
        '''
        gets the task completed for the employee,
        the task length cannot be greater than 30 characters long.
        '''
        while True:
            try:
                task = input('Enter task performed. Task Entries '
                             'cannot be more than 30 characters long : ')
                if task == '':
                    raise Exception('\nYou must enter a task!')
                elif len(task) > 30:
                    raise Exception('\nA task cannot be more '
                                    'than 30 characters long!')
                else:
                    return task
            except Exception as error:
                print(error)
            except ValueError:
                print('Invalid entry, try again!')

    def get_date_started(self):
        ''' get the time the employee started the task'''
        while True:
            try:
                date_input = input('Please enter date and date you started '
                                   'working, please use - dd/mm/yy hh:mm : ')
                date_started = datetime.datetime.strptime(date_input,
                                                          '%d/%m/%y %H:%M')
                if date_started >= datetime.datetime.now():
                    raise Exception('\nThe start date cannot be in the future!\n')
                else:
                    return date_started
            except Exception as error:
                print(error)
            except ValueError:
                print('\nInvalid entry. The date entered must use '
                      'the format dd/mm/yy hh:mm\n')

    def get_date_completed(self, date_started):
        ''' get the time the employee completed the task'''
        while True:
            try:
                date_input = input('Please enter the date and time you '
                                   'completed, please use - dd/mm/yy hh:mm : ')
                date_completed = datetime.datetime.strptime(date_input,
                                                            '%d/%m/%y %H:%M')
                if date_completed <= date_started or date_completed >= datetime.datetime.now():
                    raise Exception('\nThe completed date cannot be before the '
                                    'start date or after the current date '
                                    'and time!\n')
                else:
                    return date_completed
            except Exception as error:
                print(error)
            except ValueError:
                print('\nInvalid entry. The date entered must use the '
                      'format dd/mm/yy hh:mm\n')

    def get_total_time(self, date_started, date_completed):
        ''' calculate the total time spent on the task'''
        time_taken = date_completed - date_started
        time_taken_seconds = time_taken.total_seconds()

        mins, secs = divmod(time_taken_seconds, 60)
        hours, mins = divmod(mins, 60)
        time_str = '{} hours {} minutes'.format(hours, mins)

        return round(time_taken_seconds), time_str

    def get_notes(self):
        '''uses a system command to get end user notes'''
        print('Enter your task notes - press Ctrl+d when finished\n')
        data = sys.stdin.read().strip()
        if data:
            return data

    def find_by_employee(self):
        '''Find entries by employee'''
        employee_dict = {}
        employee_dict = OrderedDict(employee_dict)
        employee_list = []
        ctr = 1

        clear_screen()
        worklogs = Entry.select().order_by(Entry.employee_name.desc())

        # Fill out a temp dict with a list of all employees - remove duplicates
        for work_log in worklogs:
            if work_log.employee_name.upper() not in employee_list:
                employee_dict.update({str(ctr) : work_log.employee_name})
                employee_list.append(work_log.employee_name.upper())
                ctr += 1

        # print a menu to choose from
        print('Employee List \n')
        for key, value in employee_dict.items():
            print('{} {}'.format(key, value))

        while True:
            try:
                employee_id = input('\nPlease select an employee ID from the list : ')
                if employee_id == '':
                    raise Exception('Invalid entry, you must select a valid Employee ID : ')
                elif employee_id.isalpha():
                    raise Exception('Invalid entry, you must select a valid Employee ID :')
                elif int(employee_id) <= 0 or int(employee_id) >= int(ctr):
                    raise Exception('Invalid entry, choose an ID'
                                    'between 1 to {}'.format(ctr))
                else:
                    search_query = employee_dict.get(employee_id)
                    entries = Entry.select().order_by(Entry.employee_name.desc())
                    entries = entries.where(Entry.employee_name.contains \
                                        (search_query))
                    search_message = '\n The following task(s) were logged by {}' \
                                     ' :\n'.format(search_query)
                    self.display_worklogs(entries, search_message)
                    break
            except Exception as error:
                print(error)
            except ValueError:
                print('Invalid entry, try again!')

    def find_by_date(self):
        '''Find entries by date'''
        date_dict = {}
        date_dict = OrderedDict(date_dict)
        date_list = []
        ctr = 1

        clear_screen()
        worklogs = Entry.select().order_by(Entry.employee_name.desc())

        # Fill out a temp dict with a list of current start dates - remove duplicates
        for work_log in worklogs:
            if work_log.date_started not in date_list:
                date_dict.update({str(ctr) : work_log.date_started})
                date_list.append(work_log.date_started)
                ctr += 1

        # print a menu to choose from
        print('Task Date List \n')
        for key, value in date_dict.items():
            print('{} {}'.format(key, value))

        # Get a valid input from the user
        while True:
            try:
                date_id = input('\nPlease choose a date_id from the list to search entries : ')
                if date_id == '':
                    raise Exception('Invalid entry, you must select a valid date_id : ')
                elif not date_id.isnumeric():
                    raise Exception('Invalid entry, you must select a valid date_id : ')
                else:
                    search_query = date_dict.get(date_id)
                    entries = Entry.select().order_by(Entry.employee_name.desc())
                    entries = entries.where(Entry.date_started == search_query)
                    search_message = '\n The following tasks(s) started on {}' \
                                     ' :\n'.format(search_query)
                    self.display_worklogs(entries, search_message)
                    break
            except Exception as error:
                print(error)
            except ValueError:
                print("Invalid entry. Try again!")

    def find_by_duration(self):
        '''Find entries by time spent'''
        while True:
            try:
                num_minutes = input('\n Please enter the exact number, '
                                    'or a range of minutes for a task performed '
                                    '- e.g 100 or 100 - 300 : ')
                if num_minutes == '' or num_minutes.isalpha():
                    raise Exception('Invalid entry, you must enter a number :')
                elif re.match(r'\d+\s?-\s?\d+', num_minutes):
                    # we have a match on the range on minutes
                    # split the string on '-' and strip away any spaces
                    minute_range = num_minutes.strip().split('-')
                    entries = Entry.select().order_by(Entry.employee_name.desc())
                    entries = entries.where(Entry.time_taken / 60 \
                                            >= int(minute_range[0]) \
                                            & Entry.time_taken / 60 \
                                            <= int(minute_range[1]))
                    search_message = '\nThe following tasks where within your time range!'
                    self.display_worklogs(entries, search_message)
                    break
                else:
                    # check the timesheet list for entries with exact match
                    entries = Entry.select().order_by(Entry.employee_name.desc())
                    entries = entries.where((Entry.time_taken / 60) == int(num_minutes))
                    search_message = '\nThe following tasks matched the time taken!\n'
                    self.display_worklogs(entries, search_message)
                    break
            except Exception as error:
                print(error)
            except ValueError:
                print("Invalid entry. Try again!")

    def find_by_lookup(self):
        '''Find entries by lookup'''
        while True:
            try:
                search_query = input('Please enter a string you would '
                                     'like to search for i.e. '
                                     '"'"Completed database cleanup"'" : ')
                if search_query == '':
                    raise Exception('Invalid entry, you must enter a '
                                    'string to search for!')
                else:
                    entries = Entry.select().order_by(Entry.employee_name.desc())
                    entries = entries.where((Entry.completed_task.contains(search_query) | \
                                             (Entry.notes.contains(search_query))))
                    search_message = 'The following timesheets met your search criteria!\n'
                    self.display_worklogs(entries, search_message)
                    break
            except Exception as error:
                print(error)
            except ValueError:
                print("Invalid entry. Try again!")

    def display_worklogs(self, entries, message):
        '''Dispalys all the worklogs defined in a query'''
        print(message)
        if entries:
            for entry in entries:
                print(Constants.GREEN + '\n' + '*' * 50 + '\n')
                print(Constants.GREEN + ' Employee Name: {} | Task Completed: {}' \
                    .format(entry.employee_name, entry.completed_task))
                print(Constants.GREEN + ' Date Started: {} | Time Taken: {}' \
                    .format(entry.date_started, entry.time_string))
                print(Constants.GREEN + ' Notes: {} '.format(entry.notes))

                print('\n' + Constants.ENDC)
                print('n. next entry')
                print('d. delete entry')
                print('q. return to main menu')

                next_action = input('\nChoose Action [Ndq] : ').lower().strip()
                if next_action == 'q':
                    break
                elif next_action == 'd':
                    self.delete_entry(entry)
        else:
            input(Constants.GREEN + '\n\n No entries met your search criteria. '
                  'Press enter to continue' + Constants.ENDC)

    def quit(self):
        '''Quit Worklog'''
        sys.exit()

if __name__ == '__main__':
    WorkLog().worklog_run()
