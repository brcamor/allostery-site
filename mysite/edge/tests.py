from django.test import TestCase
from django.core.urlresolvers import resolve
from edge.views import home_page, chain_setup, ligand_setup
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

class ProteinChainSetupTest(TestCase):

    def setUp(self):
        self.engine = import_module(settings.SESSION_ENGINE)
        
    def test_chain_setup_uses_correct_template(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['pdb_id'] = '1SC1'
        request.session = self.engine.SessionStore(None)
        
        response = chain_setup(request)
        
        self.assertTemplateUsed(response, 'chain_setup.html')

    def test_chain_setup_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['pdb_id'] = '1SC1'
        request.session = self.engine.SessionStore(None)

        response = chain_setup(request)

        expected_html = render_to_string(
            'chain_setup.html', 
            {
                'pdb_id' : '1SC1', 
                'chain_map' : [('INTERLEUKIN-1 BETA CONVERTASE', 'A'),
                               ('INTERLEUKIN-1 BETA CONVERTASE', 'B')]
            }
        )

        self.assertEqual(response.content.decode(), expected_html)
        
class ProteinLigandSetupTest(TestCase):

    def setUp(self):
        self.engine = import_module(settings.SESSION_ENGINE)

    def test_ligand_setup_uses_correct_template(self):
        
        request = HttpRequest()
        request.method = 'POST'
        request.POST['chains'] = ['A', 'B']
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '1SC1'

        response = ligand_setup(request)

        self.assertTemplateUsed(response, 'ligand_setup.html')

        
