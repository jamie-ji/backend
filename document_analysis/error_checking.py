from django.contrib.auth.models import User
import language_tool_python
from base.models import DocumentErrorDetail
# from base.api.serializers import DocumentErrorSerializer
import requests
from datetime import datetime as dt
class ErrorCheck:
    """
    Class for linguistic error checking.
    It invokes either Ginger or language_tool.

    Attributes:
        api_type (str): The type of API to use for error checking (language_tool or ginger).
        language_longcode (str): The language code in long format ('en-AU',... for language_tool;'US'/'UK' for ginger).

    Methods:
        __init__: Initialize the ErrorCheck class with the chosen API type and language code.
        check: Perform linguistic error checking based on the chosen API type.
        language_tool_check: Perform error checking using the language_tool API.
        ginger_check: Perform error checking using the Ginger API.
    """
    def __init__(self,api_type='language_tool',language_longcode='en-AU'):
        self.language_longcode = language_longcode
        self.api_type = api_type
        if api_type == 'language_tool':
            self.tool = language_tool_python.LanguageTool(self.language_longcode)
        elif api_type == 'ginger':
            # ginger's classification of the correction into one of the following main categories
            self.correction_main_categories_dict = {
                1:"Spelling",
                2:"Misused Word",
                3:"Grammar",
                4:"Synonym",
                5:"Recommendation",
                6:"Punctuation"
            }
            # ginger's full list of category
            self.correction_all_categories_dict = {1: 'SplitAndMerge', 2: 'CommonAndProperNouns', 5: 'Pronouns', 12: 'IndefiniteArticle',
             13: 'DefiniteArticle', 15: 'Tenses', 18: 'PresentProgressive', 19: 'PastSimple', 20: 'Future',
             21: 'SubjectVerbAgreement', 23: 'AdverbialModifiers', 29: 'Prepositions',
             30: 'PrepositionsInOnAtConfusion', 31: 'Spelling', 32: 'UnneededPreposition', 34: 'PresentSimple',
             35: 'PresentPerfect', 36: 'PastProgressive', 37: 'PastPerfect', 38: 'TheInfinitive', 39: 'Participles',
             40: 'Punctuation', 42: 'Plurality', 43: 'ConsecutiveNouns', 44: 'UkUs',
             45: 'BeginningOfSentenceCapitalization', 46: 'Misused', 47: 'DoubleWords', 48: 'Synonyms',
             49: 'CommaAddition', 50: 'ComparativeSuperlative', 51: 'QuestionMarkAddition', 100: 'Vocabulary',
             102: 'InformalLanguage', 103: 'OverusedWord', 104: 'PassiveVoice', 105: 'NumeralSpellingOut'}

    def check(self, text):
        """
        Perform linguistic error checking based on the chosen API type.
        Args:
            # document_id (int) discarded: The ID of the document being checked,
            text (str): The text to be checked for errors.

        Returns:
            list: A list of error details in the form of DocumentErrorDetail objects.
            or response text if there's exception from APIs.
        """
        if self.api_type == 'language_tool':
            return self.language_tool_check(text)
        elif self.api_type == 'ginger':
            return self.ginger_check(text)
    def language_tool_check(self,text):
        # document = Document.objects.get(pk = document_id)
        matches = self.tool.check(text)
        result = []
        for match in matches:
            # For better accuracy and application in the future,we may need the premium version
            # attr_dict = vars(match)
            # for key in attr_dict.keys():
            #     print("{}   -->  {}".format(key,attr_dict[key]))
            # just choose the first replacement right now, wait for clarification from clients
            replacement = match.replacements[0] if len(match.replacements) > 0 else ""
            document_error = DocumentErrorDetail(check_time=dt.now(),error_type=match.category,error_sub_type=match.ruleId
                                           ,error_msg=match.message,sentence=match.sentence,char_position_in_text_from=match.offset
                                           ,char_position_in_text_to= match.offset + match.errorLength
                                           ,replacements=[text[match.offset :match.offset+ match.errorLength],replacement])
            # document_error.save()
            # serializer = DocumentErrorSerializer(document_error)
            # result.append(serializer.data)
            result.append(document_error)
        return result
    def ginger_check(self,text):
        # API key from Ginger Software
        API_KEY = "917c943b-ed2f-41b1-a251-1303d17dc515"
        # Construct the request URL and headers
        ENDPOINT_URL = "https://prevprod.gingersoftware.com/correction/v1/document"
        headers = {
            "Content-Type": "text/plain",
        }
        # Define the URL parameters
        # Ginger just support UK and US right now in lang
        lang = "Indifferent" if self.language_longcode not in {"UK","US"} else self.language_longcode
        params = {
            "apiKey": API_KEY,
            "lang": lang,
            "generateSynonyms": "false",
            "generateRecommendations": "false",
            "avoidCapitalization": "false",
            "emitCategoryDescription": "true"
        }
        # Make the POST request
        response = requests.post(ENDPOINT_URL, headers=headers, params=params, data=text)
        # response = requests.post(ENDPOINT_URL, headers=headers,data=text)
        # print("ginger response:")
        # print(response.json())
        if response.status_code == 200:
            data = response.json()
            # Extract corrections
            corrections = data["GingerTheDocumentResult"]["Corrections"]
            #confidence of the correction defined by ginger, this variable should be configured by clients in their settings
            CONFIDENCE = 3
            result = []
            # Iterate through corrections
            for correction in [corr for corr in corrections if corr["Confidence"] >= CONFIDENCE]:
                error_type = self.correction_main_categories_dict[correction["CorrectionType"]]
                error_sub_type = self.correction_all_categories_dict[correction["TopCategoryId"]]
                error_msg = correction["TopCategoryIdDescription"]
                sentence = correction["LrnFrg"]
                char_position_in_text_from = correction["From"]
                char_position_in_text_to = correction["To"]
                mistake_text = correction["MistakeText"]
                replacement = correction["Suggestions"][0]["Text"] if len(correction["Suggestions"]) > 0 else ""
                replacements = [mistake_text,replacement]
                # document = Document.objects.get(pk=document_id)
                document_error = DocumentErrorDetail(check_time=dt.now(),error_type=error_type,error_sub_type=error_sub_type,sentence=sentence,error_msg = error_msg,char_position_in_text_from=char_position_in_text_from,char_position_in_text_to= char_position_in_text_to,replacements=replacements)
                # document_error.save()
                # serializer = DocumentErrorSerializer(document_error)
                # result.append(serializer.data)
                result.append(document_error)
            return result
        else:
            return response.text