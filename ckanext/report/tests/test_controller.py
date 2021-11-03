# encoding: utf-8

from nose.tools import (assert_equal,
                        with_setup)

from ckan.tests import helpers


def _setup_function(self):
    self.app = helpers._get_test_app()


@with_setup(_setup_function)
class TestController():

    def test_report_index(self):
        self.app.get('/report', status=[200])

    def test_report_index_redirect(self):
        r = self.app.get('/reports', status=[301, 302])
        assert_equal(r.location, '/report')
