from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
import sys
from django.test import LiveServerTestCase

class NewVisitorTest(LiveServerTestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_choose_a_protein_and_pull_info_from_PDB(self):

        # Ben decides to check out the homepage of a new protein
        # analysis webserver
        self.browser.get(self.live_server_url)

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

        check_box = self.browser.find_element_by_id('chain_checkbox_1').click()
        check_box = self.browser.find_element_by_id('chain_checkbox_2').click()
        check_box = self.browser.find_element_by_id('chain_checkbox_3').click()

        self.browser.find_element_by_id('continue_button').click()
        
        time.sleep(2)
        
        pdb_url = self.browser.current_url
        self.assertRegexpMatches(pdb_url, '/ligands')

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual('Protein Set-up: 2HBQ', header_text)

        header_lead_text = self.browser.find_element_by_id('header_lead').text
        self.assertEqual(
            'Select the ligands you would like to include in the analysis', 
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


        # He notices the button saying "Download results" and clicks this - a
        # selection of files are downloaded to his computer and 

        # Satisfied, he decides that the developer of the site should be
        # nominated for a Nobel Prize

