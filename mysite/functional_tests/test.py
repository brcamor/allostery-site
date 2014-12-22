from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
import sys

class NewVisitorTest(unittest.TestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_choose_a_protein_and_pull_info_from_PDB(self):

        # Ben decides to check out the homepage of a new protein
        # analysis webserver
        self.browser.get('http://localhost:8000')

        # He notices the page title and header mention allosteric 
        # site and pathway prediction
        self.assertIn('Allosteric', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Allosteric', header_text)

        # He is invited to enter a PDB ID number 
        inputbox = self.browser.find_element_by_id('id_pdb_id')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'PDB ID'
            )

        # He types "1SC1" into a text box
        inputbox.send_keys('1SC1')

        # When he hits enter he is taken to a new URL, the page now
        # shows a JMol applet with his selected protein and forms
        # where he can select which residues he would like as the source
        # atoms
        inputbox.send_keys(keys.ENTER)
        pdb_url = self.browser.current_url
        self.assertRegex(pdb_url, '/proteins/1SC1/.+')

        # Now he hits "Run" and is taken to a new URL where there is a JMol
        # applet showing the protein coloured by quantile scores

        # He notices the button saying "Download results" and clicks this - a
        # selection of files are downloaded to his computer and 

        # Satisifed he decides that the developer of the site should be
        # nominated for a Nobel Prize

