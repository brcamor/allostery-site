from django.test import TestCase
from django.core.urlresolvers import resolve
from edge.views import home_page
from django.http import HttpRequest
from django.template.loader import render_to_string

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
        request = HttpRequest()
        request.method = 'POST'
        request.POST['pdb_id'] = '1SC1'

        response = home_page(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/proteins/the-only-protein-in-the-world')
        self.assertEqual(response.session['pdb_id'], '1SC1')

class ProteinSetupTest(TestCase):

    def test_uses_different_template(self):
        response = self.client.get('/proteins/the-only-protein-in-the-world')
        self.assertTemplateUsed(response, 'setup.html')

    def test_displays_protein_name(self):
        response = self.client.get('/proteins/the-only-protein-in-the-world/')
        expected_html = render_to_string('setup.html')
        self.assertContains(response, expected_html)
