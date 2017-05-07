# unit test file for worklog.py

import datetime
import unittest
from unittest.mock import Mock
from unittest.mock import patch

from peewee import *


import worklog

TEST_WORKLOGS = [
    {
        'Employee Name': 'Stuart McIntosh',
        'Task Completed': 'Completed database',
        'Date Started': '01/05/17 09:15',
        'Date Completed': '01/05/17 10:00',
        'Time Taken': 2700,
        'Time String': '0.0 hours 45.0 minutes',
        'Notes': 'Bunch of text'
    },
    {
        'Employee Name': 'Milka McIntosh',
        'Task Completed': 'Walked the dog',
        'Date Started': '2017-05-01 12:15:00',
        'Date Completed': '2017-05-01 12:45:00',
        'Time Taken': 1800,
        'Time String': '0.0 hours 30.0 minutes',
        'Notes': 'Bunch of text',
    }
]

worklog_test_db = SqliteDatabase('worklog_test.db')

class Entry(Model):
    employee_name = CharField(max_length=255)
    completed_task = CharField(max_length=30)
    date_started = DateTimeField()
    date_completed = DateTimeField()
    notes = TextField()
    time_taken = IntegerField()
    time_string = CharField()

    class Meta:
        database = worklog_test_db


class WorkLogTests(unittest.TestCase):
    ''''Main test class for WorkLog'''

    def setUp(self):
        ''' initalise in memory database to run the tests'''
        database = worklog_test_db
        worklog_test_db.connect()
        worklog_test_db.create_tables([Entry], safe=True)

    def test_check_user_table(self):
        ''' test to make sure that the database table is created '''
        assert Entry.table_exists()


    def test_create_db_entries(self):
        ''' test the creation of tables in the database'''
        for work in TEST_WORKLOGS:
            Entry.create(employee_name=work['Employee Name'],
                         completed_task=work['Task Completed'],
                         date_started=work['Date Started'],
                         date_completed=work['Date Completed'],
                         notes=work['Notes'],
                         time_taken=work['Time Taken'],
                         time_string=work['Time String'])

        # test a couple of entries to ensure that waht we stored is what we think
        self.assertEqual(Entry.get().employee_name, TEST_WORKLOGS[0]['Employee Name'])
        self.assertEqual(Entry.get().date_started, TEST_WORKLOGS[0]['Date Started'])

    def test_get_employee_name(self):
        ''' Tests to ensure we get a valid employee name back
        from the user input, the first test check it matches a regex of
        'firstname lastname'
        '''
        with unittest.mock.patch('builtins.input',
                                 side_effect=['', 'Stuart', 'Stuart McIntosh']):
            self.assertEqual(worklog.WorkLog().get_employee_name(),
                             TEST_WORKLOGS[0]['Employee Name'])

    def test_get_task(self):
        ''' tests to ensure we get a valid task back from the user'''
        with unittest.mock.patch('builtins.input',
                                 side_effect=['',
                                              '1234567890123456789012345678901',
                                              'Completed database']):
            self.assertEqual(worklog.WorkLog().get_task(),
                             TEST_WORKLOGS[0]['Task Completed'])

    def test_get_date_started(self):
        ''' test to ensure we have a valid date time from the user'''
        with unittest.mock.patch('builtins.input',
                                 side_effect=['',
                                              '01-05-17 12:00',
                                              '01.05.17 12:00',
                                              '01/05/2017 12:00',
                                              '0105-17 12:00',
                                              '12/05/17 12:00',
                                              '01/05/17 25:00',
                                              '01/05/17 09:15']):

            self.assertEqual(worklog.WorkLog().get_date_started(),
                             datetime.datetime.strptime(TEST_WORKLOGS[0]
                                                        ['Date Started'],
                                                        '%d/%m/%y %H:%M'))

    def test_get_date_completed(self):
        ''' test to ensure we have a valid date time from the user'''
        date_started = datetime.datetime.strptime(Entry.get().date_started,
                                                  '%d/%m/%y %H:%M')
        with unittest.mock.patch('builtins.input',
                                 side_effect=['',
                                              '12-05-17 12:00',
                                              '12.05.17 12:00',
                                              '12/05/2017 12:00',
                                              '1205-17 12:00',
                                              '12/05/17 25:00',
                                              '01/05/17 10:00']):

            self.assertEqual(worklog.WorkLog().get_date_completed(date_started),
                             datetime.datetime.strptime(TEST_WORKLOGS[0]
                                                        ['Date Completed'],
                                                        '%d/%m/%y %H:%M'))

    def test_get_total_time(self):
        ''' test toatl time calculation '''
        date_completed = datetime.datetime.strptime(Entry.get().date_completed,
                                                    '%d/%m/%y %H:%M')

        date_started = datetime.datetime.strptime(Entry.get().date_started,
                                                  '%d/%m/%y %H:%M')
        time_taken = date_completed - date_started
        time_taken_seconds = time_taken.total_seconds()
        mins, secs = divmod(time_taken_seconds, 60)
        hours, mins = divmod(mins, 60)
        time_str = '{} hours {} minutes'.format(hours, mins)
        self.assertEqual(time_taken_seconds, TEST_WORKLOGS[0]['Time Taken'])
        self.assertEqual(time_str, TEST_WORKLOGS[0]['Time String'])

    def test_find_by_employee(self):
        ''' test find employee '''
        search_query = 'Stuart McIntosh'
        entries = Entry.select().order_by(Entry.date_started.desc())
        entries = entries.where(Entry.employee_name.contains(search_query))

        with unittest.mock.patch('builtins.input',
                                 side_effect=['', 'Stuart', 'Stuart McIntosh']):
            self.assertEqual(worklog.WorkLog().get_employee_name(), search_query)

    def test_find_by_date(self):
        ''' test find by date '''
        search_query = '01/05/17 09:15'
        entries = Entry.select().order_by(Entry.employee_name.desc())
        entries = entries.where(Entry.date_started == search_query)

        with unittest.mock.patch('builtins.input',
                                 side_effect=['', '20175-01', '01/05/17 09:15']):
            self.assertEqual(worklog.WorkLog().get_date_started(),
                             datetime.datetime.strptime(TEST_WORKLOGS[0]
                                                        ['Date Started'],
                                                        '%d/%m/%y %H:%M'))

    def test_find_by_duration(self):
        ''' test find by duration '''
        num_minutes = '1 - 100'
        minute_range = num_minutes.strip().split('-')
        entries = Entry.select().order_by(Entry.employee_name.desc())
        entries = entries.where(Entry.time_taken / 60
                                >= int(minute_range[0])
                                & Entry.time_taken / 60
                                <= int(minute_range[1]))

        date_started = datetime.datetime.strptime(TEST_WORKLOGS[0]['Date Started'],
                                                  '%d/%m/%y %H:%M')
        date_completed = datetime.datetime.strptime(TEST_WORKLOGS[0]['Date Completed'],
                                                    '%d/%m/%y %H:%M')
        with unittest.mock.patch('builtins.input',
                                 side_effect=['', '10', '1 - 100']):
            self.assertEqual(worklog.WorkLog().get_total_time(date_started, date_completed),
                             TEST_WORKLOGS[0]['Time Taken'],
                             TEST_WORKLOGS[0]['Time String'])

    def test_find_by_lookup(self):
        ''' test find by text serach'''
        search_query = 'Completed database'
        entries = Entry.select().order_by(Entry.employee_name.desc())
        entries = entries.where((Entry.completed_task.contains(search_query) | \
                                 (Entry.notes.contains(search_query))))

        with unittest.mock.patch('builtins.input',
                                 side_effect=['', 'Completed database', 'Completed database']):
            self.assertRaises(ValueError, worklog.WorkLog().find_by_lookup(), '')
        '''                         
        with unittest.mock.patch('builtins.input',
                                 side_effect=['', 'Completed database', 'Completed database']):
            self.assertEqual(worklog.WorkLog().find_by_lookup(),
                             TEST_WORKLOGS[0]['Task Completed'])
        '''                     

if __name__ == '__main__':
    unittest.main()
