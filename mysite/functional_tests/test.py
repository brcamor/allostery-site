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
        self.assertRegexpMatches(pdb_url, '/proteins/1SC1/chains')

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual('Protein Set-up: 2HBQ', header_text)
        
        table = self.browser.find_element_by_id('id_protein_table')
        rows = table.find_elements_by_tag_name('td')
        row_text = [row.text for row in rows]
        self.assertEqual('Molecule name', row_text[0])
        self.assertEqual('Chain', row_text[1])
        self.assertEqual('Selected', row_text[2])
        self.assertEqual('1: CASPASE-1', row_text[3])
        self.assertEqual('A', row_text[4])
        self.assertEqual('2: CASPASE-1INTERLEUKIN-1 BETA CONVERTASE', row_text[6])
        self.assertEqual('B', row_text[7])
        self.assertEqual('3: N-[(BENZYLOXY)CARBONYL]-L-VALYL-N-[(2S)-1-CARBOXY-4-FLUORO',
                         row_text[9])
        self.assertEqual('C', row_text[10])

        # He also notices that there are checkboxes where he can select the chains he
        # wants to include in the analysis.  He selects all three checkboxes and hits
        # 'Next'.  This takes him to a new URL, which shows him the HETATM entries in
        # the pdb file


        # Now he selects selects both chains and clicks "Next", he is taken to
        # a new page where he is shown a list of the molecules in the protein
        # There are is 

        # He notices the button saying "Download results" and clicks this - a
        # selection of files are downloaded to his computer and 

        # Satisfied, he decides that the developer of the site should be
        # nominated for a Nobel Prize

