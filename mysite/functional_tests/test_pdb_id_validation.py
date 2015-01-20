from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import unittest
from unittest import skip
import sys
from django.test import TestCase
import proteinnetwork as pn

class PDBIDValidationTest(FunctionalTest):

    def test_cannot_search_for_list_items(self):
        # Ben goes to the home page and accidentally tries to search
        # an empty PDB ID. He hits Enter on the empty input box.
        
        # The home page refreshes, and there is an error message saying
        # that search items cannot be blank
        
        self.fail('write me!')

    def test_cannot_search_for_invalid_PDB_ID(self):
        # Ben goes to the home page and tries to search for an 
        # invalid PDB ID. He hits Enter on the empty input box.
        
        # The home page refreshes, and there is an error message saying
        # that the entered text is not a valid PDB ID.

        self.fail("write me!")
        
