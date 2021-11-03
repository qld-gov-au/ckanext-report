# encoding: utf-8

from nose.tools import (assert_equal,
                        assert_in,
                        assert_regexp_matches,
                        with_setup)

from ckan.tests import helpers


def _setup_function(self):
    self.app = helpers._get_test_app()


@with_setup(_setup_function)
class TestController():

    def test_report_index(self):
        response = self.app.get('/report', status=200)
        assert_regexp_matches(response.html.head.title, 'Reports')

    def test_report_index_redirect(self):
        response = self.app.get('/reports', status=[301, 302])
        assert_equal(response.location.split('/')[3], 'report')
