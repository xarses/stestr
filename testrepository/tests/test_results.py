#
# Copyright (c) 2010 Testrepository Contributors
#
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

from datetime import datetime
from threading import Semaphore

from testtools import (
    TestCase,
    TestResult,
    ThreadsafeForwardingResult,
    )

from testrepository.results import TestResultFilter
from testrepository.ui import BaseUITestResult
from testrepository.ui.model import UI


class ResultFilter(TestCase):

    def test_addSuccess_increases_count(self):
        result = BaseUITestResult(UI(), lambda:1)
        filtered = TestResultFilter(result)
        filtered.startTest(self)
        filtered.addSuccess(self)
        filtered.stopTest(self)
        self.assertEqual(1, result.testsRun)

    def test_time_goes_through_for_success(self):
        # Success is normally filtered out, but we still want to get the time
        # events forwarded to the underlying result because they represent the
        # most up-to-date time information.
        result = TestResult()
        filtered = TestResultFilter(result)
        filtered.startTestRun()
        filtered.time(datetime(2011, 1, 1, 0, 0, 1))
        filtered.startTest(self)
        filtered.time(datetime(2011, 1, 1, 0, 0, 2))
        filtered.addSuccess(self)
        filtered.time(datetime(2011, 1, 1, 0, 0, 3))
        filtered.stopTest(self)
        filtered.stopTestRun()
        self.assertEqual(datetime(2011, 1, 1, 0, 0, 3), result._now())

    def test_time_going_through_threadsafe_filter(self):
        # ThreadsafeForwardingResult discards time() output that is not bound
        # specifically to the start or end of a test.  This test is here to
        # document that behaviour and act as a flag if the behaviour changes.
        result = TestResult()
        filtered = ThreadsafeForwardingResult(
            TestResultFilter(result), Semaphore(1))
        filtered.startTestRun()
        filtered.time(datetime(2011, 1, 1, 0, 0, 1))
        filtered.startTest(self)
        filtered.time(datetime(2011, 1, 1, 0, 0, 2))
        filtered.addSuccess(self)
        # This will be ignored.
        filtered.time(datetime(2011, 1, 1, 0, 0, 3))
        filtered.stopTest(self)
        filtered.stopTestRun()
        self.assertEqual(datetime(2011, 1, 1, 0, 0, 2), result._now())
