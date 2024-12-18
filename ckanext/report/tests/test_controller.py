# encoding: utf-8

from ckan.tests import helpers


def _get_response_body(response):
    ''' Extract the response body of a Webtest or Flask response as text.
    '''
    if hasattr(response, 'html'):
        return response.html.renderContents()
    elif hasattr(response, 'get_data'):
        return response.get_data(as_text=True)
    else:
        raise Exception("Unrecognised response object: [{}]".format(response))


class TestController():

    def setup_method(self, test_function):
        self.app = helpers._get_test_app()

    def test_report_index(self):
        response = self.app.get('/report', status=200)
        assert '<title>Reports' in _get_response_body(response)

    def test_report_view(self):
        response = self.app.get('/report/tagless-datasets', status=200)
        assert '<title>Tagless datasets' in _get_response_body(response)
