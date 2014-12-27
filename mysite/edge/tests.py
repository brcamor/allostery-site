from django.test import TestCase
from django.core.urlresolvers import resolve
from edge.views import home_page
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.importlib import import_module

class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('home.html')
        self.assertEqual(response.content.decode(), expected_html)

    def test_home_page_redirects_after_POST_request(self):
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request = HttpRequest()
        request.method = 'POST'
        request.POST['pdb_id'] = '1SC1'
        request.session = engine.SessionStore(session_key)

        response = home_page(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/proteins/1SC1/chains')
        self.assertEqual(request.session['pdb_id'], '1SC1')

class ProteinChainSetupTest(TestCase):

    def setUp(self):
        self.client.session['pdb_id'] = '1SC1'

    def test_uses_different_template(self):
        response = self.client.get('/proteins/1SC1/chains')
        self.assertTemplateUsed(response, 'chain_setup.html')

    def displays_protein_name(self):
        response = self.client.get('/proteins/1SC1/chains')
        self.assertContains(response, '1SC1')
        
