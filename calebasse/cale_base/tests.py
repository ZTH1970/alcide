"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from datetime import datetime, timedelta


class UserTest(TestCase):

    def test_create_work_event(self):
        """docstring for test_create_event"""
        from calebasse.cale_base.models import CalebasseUser
        user = CalebasseUser()
        user.add_work_event('MO', datetime(2016,10,2,10), datetime(2016,10,2,12),
                datetime(2018,1,1))
        self.assertEqual(str(user.event), 'work MO')
        event = user.event.occurrence_set.all()[0]
        self.assertEqual(event.end_time - event.start_time, timedelta(0, 7200))

