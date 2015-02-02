from django.test import TestCase
from django.core.urlresolvers import resolve
from edge.views import (home_page,
                        chain_setup,
                        hetatm_setup, 
                        source_setup, 
                        results) 
from django.http import HttpRequest
from django.http.request import QueryDict
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.importlib import import_module
import proteinnetwork as pn
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
 
        self.assertTemplateUsed(response, ' chain_setup.html')

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
        request.session['all_chains'] = ['A', 'B']
        _dict = {'chains' : 'A'}
        _qdict = QueryDict('', mutable=True)
        _qdict.update(_dict)
        request.POST = _qdict

        response = chain_setup(request)
        self.assertEqual(request.session.get('included_chains'), ['A'])
        self.assertEqual(request.session.get('removed_chains'), ['B'])

class ProteinHetatmSetupTest(TestCase):

    def setUp(self):
        self.engine = import_module(settings.SESSION_ENGINE)

    def test_hetatm_setup_uses_correct_template(self):
        
        request = HttpRequest()
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['included_chains'] = ['A', 'B', 'C']

        response = hetatm_setup(request)

        self.assertTemplateUsed(response, 'hetatm_setup.html')

    def test_hetatm_setup_finds_all_ligands_correctly(self):
        request = HttpRequest()
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['included_chains'] = ['A', 'B', 'C']
        request.session['removed_chains'] = []

        response = hetatm_setup(request)
        
        self.assertIn(('PHQ', 'C', '1'), request.session.get('hetatms'))
        self.assertIn(('CF0', 'C', '5'), request.session.get('hetatms'))

    def test_hetatm_setup_saves_included_ligands_correctly(self):
        request = HttpRequest()
        request.method = 'POST'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['included_chains'] = ['A', 'B', 'C']
        request.session['removed_chains'] = []
        request.session['hetatms'] = [('PHQ', 'C', '1'), ('CF0', 'C', '5')]

        _dict = {'hetatms' : '0'}
        _qdict = QueryDict('', mutable=True)
        _qdict.update(_dict)
        request.POST = _qdict

        response = hetatm_setup(request)

        self.assertIn(['1', 'C'], request.session.get('included_hetatms'))

    def test_hetatm_setup_POST_redirects_to_source_setup(self):
        request = HttpRequest()
        request.method = 'POST'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['included_chains'] = ['A', 'B', 'C']
        request.session['hetatms'] = [('PHQ', 'C', '1'), ('CF0', 'C', '5')]
        request.session['removed_chains'] = []
        
        _dict = {'hetatms' : '0'}
        _qdict = QueryDict('', mutable=True)
        _qdict.update(_dict)
        request.POST = _qdict

        response = hetatm_setup(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/source')

class ProteinSourceSetupTest(TestCase):

    def setUp(self):
        self.engine = import_module(settings.SESSION_ENGINE)
        
    def test_source_setup_uses_correct_template(self):
        
        request = HttpRequest()
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['included_chains'] = ['A', 'B', 'C']
        request.session['removed_chains'] = []

        response = source_setup(request)
        
        self.assertTemplateUsed(response, 'source_setup.html')

    def test_source_setup_shows_only_selected_chains_and_hetams(self):
        request = HttpRequest()
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['included_chains'] = ['B', 'C']
        request.session['removed_chains'] = ['A']
        request.session['included_hetatms'] = [['1', 'C']]
        request.session['removed_hetatms'] = [['5', 'C']]

        response = source_setup(request)
        residue_list = request.session['residue_list']
        print residue_list
        self.assertIn(('317', 'B'), residue_list)
        self.assertIn(('1', 'C'), residue_list)
        
        self.assertNotIn(('130', 'A'), residue_list)
        self.assertNotIn(('5', 'C'), residue_list)

    def test_source_redirects_to_results(self):
        request = HttpRequest()
        request.method = 'POST'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '1SC1'
        request.session['included_chains'] = ['A', 'B']
        request.session['removed_chains'] = ['A']
        request.session['hetatms'] = [('PHQ', 'C', '1'), ('CF0', 'C', '5')]
        request.session['residue_list'] = [('125', 'A'), ('126', 'A')]
        
        _dict = {'residues' : '0'}
        _qdict = QueryDict('', mutable=True)
        _qdict.update(_dict)
        request.POST = _qdict

        response = source_setup(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/results')


    def test_source_setup_stores_source_residues_to_session_variable(self):
        request = HttpRequest()
        request.method = 'POST'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '1SC1'
        request.session['chains'] = ['A', 'B']
        request.session['hetatms'] = [('PHQ', 'C', '1'), ('CF0', 'C', '5')]
        request.session['residue_list'] = [('125', 'A'), ('126', 'A')]
        
        _dict = {'residues' : '0'}
        _qdict = QueryDict('', mutable=True)
        _qdict.update(_dict)
        request.POST = _qdict

        response = source_setup(request)

        self.assertEqual(request.session.get('source_residues')[0], ('125', 'A'))

class ProteinResultsTest(TestCase):
    
    def setUp(self):
        self.engine = import_module(settings.SESSION_ENGINE)

    def test_results_url_resolves_to_results_view(self):
        found = resolve('/results')
        self.assertEqual(found.func, results)        

    def test_results_page_returns_correct_template(self):
        
        request = HttpRequest()
        request.method = 'GET'
        request.session = self.engine.SessionStore(None)
        request.session['pdb_id'] = '2HBQ'
        request.session['chains'] = ['A', 'B', 'C']
        request.session['hetatms'] = [('PHQ', 'C', '1'), ('CF0', 'C', '5')]
        request.session['residue_list'] = [('125', 'A'), ('126', 'A')]
        request.session['source_residues'] = [('125', 'A')]

        response = results(request)
        
        self.assertTemplateUsed(response, 'results.html')
