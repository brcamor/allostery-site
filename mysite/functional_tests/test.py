from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
import sys
from django.test import TestCase
import proteinnetwork as pn

class NewVisitorTest(TestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)        
        self.server_url = "http://155.198.224.245:8000"

    def tearDown(self):
        self.browser.quit()

    def test_can_choose_a_protein_and_pull_info_from_PDB(self):

        # Ben decides to check out the homepage of a new protein
        # analysis webserver
        self.browser.get(self.server_url)

        # He notices the page title and header mention allosteric 
        # site prediction
        self.assertIn('Allosteric', self.browser.title)
        self.assertIn('site', self.browser.title)
        self.assertIn('prediction', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Start a new protein analysis', header_text)

        header_lead_text = self.browser.find_element_by_id('header_lead').text
        self.assertEqual(
            "To begin the analysis, enter the 4-digit PDB ID of the structure you would like to analyse", 
            header_lead_text
        )

        
        # He is invited to enter a PDB ID number 
        inputbox = self.browser.find_element_by_id('id_pdb_id')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter PDB ID here'
            )

        # He types "2HBQ" into a text box
        inputbox.send_keys('2HBQ')

        # When he hits enter he is taken to a new URL, the page now
        # shows the name of the protein he wants to analyse (caspase-1)
        # and a list of the chains in the pdb file

        inputbox.send_keys(Keys.ENTER)
        import time
        time.sleep(2)
        
        pdb_url = self.browser.current_url
        self.assertRegexpMatches(pdb_url, '/chains')

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual('Protein Set-up: 2HBQ', header_text)

        header_lead_text = self.browser.find_element_by_id('header_lead').text
        self.assertEqual(
            'Select the chains you would like to include in the analysis', 
            header_lead_text
        )

        table = self.browser.find_element_by_id('id_chain_table')
        
        table_headers = table.find_elements_by_tag_name('th')
        table_header_text = [header.text for header in table_headers]
        self.assertEqual('Molecule name', table_header_text[0])
        self.assertEqual('Chain', table_header_text[1])
        self.assertEqual('Selected', table_header_text[2])

        rows = table.find_elements_by_tag_name('td')
        row_text = [row.text for row in rows]
        self.assertEqual('1: CASPASE-1', row_text[0])
        self.assertEqual('A', row_text[1])
        self.assertEqual('2: CASPASE-1', row_text[3])
        self.assertEqual('B', row_text[4])
        self.assertEqual('3: N-[(BENZYLOXY)CARBONYL]-L-VALYL-N-[(2S)-1-CARBOXY-4-FLUORO',
                         row_text[6])
        self.assertEqual('C', row_text[7])

        # He also notices that there are checkboxes where he can select the chains he
        # wants to include in the analysis.  He selects all three checkboxes and hits
        # 'Continue'.  This takes him to a new URL, which shows him the HETATM entries in
        # the pdb file

        self.browser.find_element_by_id('chain_checkbox_1').click()
        self.browser.find_element_by_id('chain_checkbox_2').click()
        self.browser.find_element_by_id('chain_checkbox_3').click()

        self.browser.find_element_by_id('continue_button').click()
        
        time.sleep(2)
        
        pdb_url = self.browser.current_url
        self.assertRegexpMatches(pdb_url, '/hetatms')

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual('Protein Set-up: 2HBQ', header_text)

        header_lead_text = self.browser.find_element_by_id('header_lead').text
        self.assertEqual(
            'Select the heteroatoms you would like to include in the analysis', 
            header_lead_text
        )
        
        table = self.browser.find_element_by_id('id_hetatm_table')
        
        table_headers = table.find_elements_by_tag_name('th')
        table_header_text = [header.text for header in table_headers]
        self.assertEqual('Name', table_header_text[0])
        self.assertEqual('Chain', table_header_text[1])
        self.assertEqual('Number', table_header_text[2])
        self.assertEqual('Selected', table_header_text[3])

        rows = table.find_elements_by_tag_name('td')
        row_text = [row.text for row in rows]
        self.assertEqual('1: CF0', row_text[0])
        self.assertEqual('C', row_text[1])
        self.assertEqual('5', row_text[2])
        
        self.assertEqual('2: PHQ', row_text[4])
        self.assertEqual('C', row_text[5])
        self.assertEqual('1', row_text[6])

        # He selects the HETATM entries he wants to include in the analysis and
        # clicks the "Continue" button.  He is taken to a new URL which
        # asks him to select the residues he would like to use as source atoms
        # in the analysis

        self.browser.find_element_by_id('hetatm_checkbox_1').click()
        self.browser.find_element_by_id('hetatm_checkbox_2').click()
       
        self.browser.find_element_by_id('continue_button').click()

        pdb_url = self.browser.current_url
        self.assertRegexpMatches(pdb_url, '/source')

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual('Protein Set-up: 2HBQ', header_text)

        header_lead_text = self.browser.find_element_by_id('header_lead').text
        self.assertEqual(
            'Select the residues you would like to use as the source in the analysis', 
            header_lead_text
        )
        
        table = self.browser.find_element_by_id('id_source_table')
        headers = table.find_elements_by_tag_name('th')
        header_text = [header.text for header in headers]
        self.assertIn('Residue number', header_text)
        self.assertIn('Chain', header_text)
        self.assertIn('Selected', header_text)

        rows = table.find_elements_by_tag_name('td')
        row_text = [row.text for row in rows]
        self.assertEqual('125', row_text[0])
        self.assertEqual('A', row_text[1])
        self.assertEqual('C', row_text[-2])
        self.assertEqual('5', row_text[-3])

        # He selects the first few residues as his source (125-128 in chain A)
        # and clicks "Continue".  He is taken to a new url "results"

        self.browser.find_element_by_id('residue_checkbox_1').click()
        self.browser.find_element_by_id('residue_checkbox_2').click()
        self.browser.find_element_by_id('residue_checkbox_3').click()
        self.browser.find_element_by_id('residue_checkbox_4').click()

        self.browser.find_element_by_id('continue_button').click()

        time.sleep(2)

        pdb_url = self.browser.current_url
        self.assertRegexpMatches(pdb_url, '/results')

        # The page soon loads and he is shown a list of the top bonds in
        # the protein by perturbation propensity and top residues by 
        # perturbation propensity

        bond_pp_table = self.browser.find_element_by_id('id_bond_pp_table')
        
        bond_pp_headers = bond_pp_table.find_elements_by_tag_name('th')
        bond_pp_headers_text = [header.text for header in bond_pp_headers]
        self.assertEqual('Atom 1', bond_pp_headers_text[0])
        self.assertEqual('Atom 2', bond_pp_headers_text[1])
        self.assertEqual('Perturbation Propensity', bond_pp_headers_text[2])
        bond_pp_rows = bond_pp_table.find_elements_by_tag_name('td')
        bond_pp_rows_text = [row.text for row in bond_pp_rows]
        self.assertEqual('VAL 133 H', bond_pp_rows_text[0])
        self.assertEqual('GLU 130 O', bond_pp_rows_text[1])

        residue_pp_table = self.browser.find_element_by_id('id_residue_pp_table')
        
        residue_pp_headers = residue_pp_table.find_elements_by_tag_name('th')
        residue_pp_headers_text = [header.text for header in residue_pp_headers]
        self.assertEqual('Residue', residue_pp_headers_text[0])
        self.assertEqual('Perturbation Propensity', residue_pp_headers_text[1])
        residue_pp_rows = residue_pp_table.find_elements_by_tag_name('td')
        residue_pp_rows_text = [row.text for row in residue_pp_rows]
        self.assertEqual('130 A', residue_pp_rows_text[0])
        self.assertEqual('133 A', residue_pp_rows_text[2])

        # He also notices an image showing the perturbation
        # propensity of bonds plotted against their distance from 
        # the source residues

        

