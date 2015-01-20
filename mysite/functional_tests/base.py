from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import unittest
from unittest import skip
import sys
from django.test import TestCase
import proteinnetwork as pn

class FunctionalTest(TestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)        
        self.server_url = "http://155.198.224.245:8000"

    def tearDown(self):
        self.browser.quit()

        

