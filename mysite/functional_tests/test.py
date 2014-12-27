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

        # He types "1SC1" into a text box
        inputbox.send_keys('1SC1')

        # When he hits enter he is taken to a new URL, the page now
        # shows the name of the protein he wants to analyse (caspase-1)
        # and a list of the chains in the pdb file

        inputbox.send_keys(Keys.ENTER)
        import time
        time.sleep(2)
        
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual('Protein Set-up: 1SC1', header_text)
        
        table = self.browser.find_element_by_id('id_protein_table')
        rows = table.find_elements_by_tag_name('td')
        row_text = [row.text for row in rows]
        self.assertEqual('Molecule name', row_text[0])
        self.assertEqual('Chain', row_text[1])
        self.assertEqual('1: INTERLEUKIN-1 BETA CONVERTASE', row_text[2])
        self.assertEqual('A', row_text[3])
        self.assertEqual('2: INTERLEUKIN-1 BETA CONVERTASE', row_text[4])
        self.assertEqual('B', row_text[5])

        pdb_url = self.browser.current_url
        self.assertRegexpMatches(pdb_url, '/proteins/1SC1/.+')

        # Now he hits "Run" and is taken to a new URL where there is a JMol
        # applet showing the protein coloured by quantile scores

        # He notices the button saying "Download results" and clicks this - a
        # selection of files are downloaded to his computer and 

        # Satisfied, he decides that the developer of the site should be
        # nominated for a Nobel Prize

