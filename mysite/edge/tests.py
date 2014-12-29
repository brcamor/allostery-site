from django.test import TestCase
from django.core.urlresolvers import resolve
from edge.views import home_page, chain_setup, hetatm_setup, source_setup
from django.http import HttpRequest
from django.http.request import QueryDict
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.importlib import import_module
import urllib

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
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '1SC1'

        response = chain_setup(request)
        
        self.assertTemplateUsed(response, 'chain_setup.html')

    def test_chain_setup_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '1SC1'

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
        
    def test_chain_setup_saves_chains_correctly(self):
        request = HttpRequest()
        request.method = 'POST'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '1SC1'
        _dict = {'chains' : ['A', 'B']}
        _qdict = QueryDict('', mutable=True)
        _qdict.update(_dict)
        request.POST = _qdict

        response = chain_setup(request)
        print request.session['chains']
        self.assertEqual(request.session.get('chains')[0], ['A', 'B'])

class ProteinHetatmSetupTest(TestCase):

    def setUp(self):
        self.engine = import_module(settings.SESSION_ENGINE)

    def test_hetatm_setup_uses_correct_template(self):
        
        request = HttpRequest()
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['chains'] = ['A', 'B', 'C']

        response = hetatm_setup(request)

        self.assertTemplateUsed(response, 'hetatm_setup.html')

    def test_hetatm_setup_finds_all_ligands_correctly(self):
        request = HttpRequest()
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['chains'] = ['A', 'B', 'C']
        
        response = hetatm_setup(request)
        
        self.assertIn(('PHQ', 'C', '1'), request.session.get('hetatms'))
        self.assertIn(('CF0', 'C', '5'), request.session.get('hetatms'))

    def test_hetatm_setup_saves_included_ligands_correctly(self):
        request = HttpRequest()
        request.method = 'POST'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '1SC1'
        request.session['chains'] = ['A', 'B']
        request.session['hetatms'] = [('PHQ', 'C', '1'), ('CF0', 'C', '5')]

        _dict = {'hetatms' : '1'}
        _qdict = QueryDict('', mutable=True)
        _qdict.update(_dict)
        request.POST = _qdict

        response = hetatm_setup(request)

        self.assertEqual(request.session.get('included_hetatms')[0], ('PHQ', 'C', '1'))

class ProteinSourceSetupTest(TestCase):

    def setUp(self):
        self.engine = import_module(settings.SESSION_ENGINE)
        
    def test_source_setup_uses_correct_template(self):
        
        request = HttpRequest()
        request.method = 'GET'
        
        response = source_setup(request)
        
        self.assertTemplateUsed(response, 'source_setup.html')
