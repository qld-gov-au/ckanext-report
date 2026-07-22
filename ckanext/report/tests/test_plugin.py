# encoding: utf-8

import pytest
from ckan.plugins import toolkit as tk
from ckan.tests import factories

import ckanext.report.model as report_model


def _assert_in_body(string, response):
    assert string in response.body


def _assert_status(res, code_int):
    if hasattr(res, 'status_code'):
        assert res.status_code == code_int
    elif hasattr(res, 'status_int'):
        assert res.status_int == code_int
    else:
        raise NotImplementedError('No status for response')


@pytest.fixture
def report_setup():
    report_model.init_tables()


@pytest.mark.ckan_config(u'ckan.plugins', u'report tagless_report')
@pytest.mark.usefixtures(u'clean_db', u'with_plugins', u'report_setup')
class TestReportPlugin(object):

    def test_report_routes(self, app):
        u"""Test report routes"""
        res = app.get(u'/report')

        _assert_in_body(u"Reports", res)

    def test_tagless_report_listed(self, app):
        u"""Test tagless report is listed on report page"""
        res = app.get(u'/report')

        _assert_in_body(u'Tagless datasets', res)
        _assert_in_body(u'href="/report/tagless-datasets"', res)

    def test_tagless_report(self, app):
        u"""Test tagless report generation"""
        res = app.get(u'/report/tagless-datasets')

        _assert_in_body(u"Datasets which have no tags.", res)
        _assert_in_body('<h3>Results</h3>', res)

    def test_tagless_report_csv(self, app):
        u"""Test tagless report generation"""
        org = factories.Organization()
        dataset1 = factories.Dataset(owner_org=org['id'])  # noqa F841
        dataset2 = factories.Dataset(owner_org=org['id'])  # noqa F841

        res = app.get(u'/report/tagless-datasets?format=csv')
        _assert_status(res, 200)

    def test_tagless_report_json(self, app):
        u"""Test tagless report generation"""
        org = factories.Organization()
        dataset1 = factories.Dataset(owner_org=org['id'])  # noqa F841
        dataset2 = factories.Dataset(owner_org=org['id'])  # noqa F841
        res = app.get(u'/report/tagless-datasets?format=json')
        _assert_status(res, 200)

    def test_tagless_report_refresh_ok(self, app):
        u"""Test tagless refresh report"""
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])  # noqa F841
        if tk.check_ckan_version(min_version="2.10"):
            user = factories.SysadminWithToken()
            headers = {"Authorization": user["token"]}
            res = app.post(url='/report/tagless-datasets', headers=headers)
        else:
            user = factories.Sysadmin()
            env = {'REMOTE_USER': user['name'].encode('ascii')}
            res = app.post('/report/tagless-datasets', extra_environ=env)

        _assert_status(res, 200)
