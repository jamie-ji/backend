import unittest
from .error_checking import ErrorCheck
from .docx_helpler import DocxReader
from .docx_helpler import DocumentErrorExporter
from base.models import DocumentErrorDetail
import os
class TestErrorCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the ErrorCheck object with test parameters
        language_tool = ErrorCheck(api_type='language_tool', language_longcode='en-AU')
        cls.language_tool = language_tool
        language_tool_local = ErrorCheck(api_type='language_tool_local', language_longcode='en-AU')
        cls.language_tool_local = language_tool_local
        ginger = ErrorCheck(api_type='ginger', language_longcode='UK')
        cls.ginger = ginger

    def test_language_tool_local_easy(self):
        # Initialize the ErrorCheck object with test parameters
        # error_checker = ErrorCheck(api_type='language_tool', language_longcode='en-AU')
        # easy one
        #result = error_checker.check("There mush be an error")
        result = self.language_tool_local.check("Once a jolly swagman camped a billabang.")
        self.assertTrue(len(result)>= 1)
        print("language_tool easy result \n {}".format(result))
    def test_language_tool_local_doc(self):
        current_directory = os.getcwd()
        # docx_file = current_directory + "/documents/user_1/Stakeholder_engagement.docx"
        docx_file = "/Users/daibo/Downloads/Year 9/Term 1/English assignments.docx"
        docx_reader = DocxReader(docx_file)
        text = docx_reader.get_text()
        result = self.language_tool_local.check(text)
        # print("language_tool doc \n result {}".format(result))
        exporter = DocumentErrorExporter(docx_file.split(".")[0]+"_lt_local.xlsx")
        exporter.export_to_excel(result)
    def test_language_tool_easy(self):
        # Initialize the ErrorCheck object with test parameters
        # error_checker = ErrorCheck(api_type='language_tool', language_longcode='en-AU')
        # easy one
        #result = error_checker.check("There mush be an error")
        result = self.language_tool.check("Once a jolly swagman camped a billabang.")
        self.assertTrue(len(result)>= 1)
        print("language_tool easy result \n {}".format(result))
    def test_language_tool_doc(self):
        current_directory = os.getcwd()
        # docx_file = current_directory + "/documents/user_1/Stakeholder_engagement.docx"
        docx_file = "/Users/daibo/Downloads/Year 9/Term 1/English assignments.docx"
        docx_reader = DocxReader(docx_file)
        text = docx_reader.get_text()
        result = self.language_tool.check(text)
        # print("language_tool doc \n result {}".format(result))
        exporter = DocumentErrorExporter(docx_file.split(".")[0]+"_lt.xlsx")
        exporter.export_to_excel(result)

    @unittest.skip("")
    def test_ginger_easy(self):
        # Write test cases for Ginger check method
        # error_checker = ErrorCheck(api_type='ginger', language_longcode='UK')
        # result = error_checker.check("There mush be an error")
        result = self.ginger.check("Once a jolly swagman camped a billabang.")
        self.assertTrue(len(result)>= 1)
        print("ginger easy result \n {}".format(result))

    @unittest.skip("")
    def test_ginger_tool_doc(self):
        # current_directory = os.getcwd()
        # docx_file = current_directory + "/documents/user_1/Stakeholder_engagement.docx"
        current_directory = os.getcwd()
        docx_file = "/Users/daibo/Downloads/Year 9/Term 1/English assignments.docx"
        docx_reader = DocxReader(docx_file)
        text = docx_reader.get_text()
        result = self.ginger.check(text)
        print("ginger doc result \n {}".format(result))
        exporter = DocumentErrorExporter(docx_file.split(".")[0] + "_ginger.xlsx")
        exporter.export_to_excel(result)
