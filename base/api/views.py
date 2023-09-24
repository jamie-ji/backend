from rest_framework.viewsets import ViewSet
from rest_framework.response import Response 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from base.models import Document, DocumentErrorDetail, DocumentErrorStat
from .serializers import DocumentSerializer, DocumentUploadSerializer, RegisterSerializer, UserSerializer, UserProfilesSerializer
from .serializers import DocumentErrorDetailSerializer, DocumentErrorStatSerializer

from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model

from document_analysis.error_checking import ErrorCheck
from django.db import models

import json

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# class MyTokenRefreshView(TokenRefreshView):
#     serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def getRoutes(request): 
    routes = []
    api = {"route" : "/api/", 
              "method" : "GET", 
              "permission_classes": "AllowAny", 
              "description": "List all the routes of the backend API"}
    routes.append(api)

    api = {"route" : "/api/token/",
              "method" : "POST", 
              "permission_classes": "AllowAny", 
              "description": "Get the token for authentication using username and password", 
              "body": "{username, password}", 
              "response": "{access, refresh}"}
    routes.append(api)

    api = {"route" : "/api/token/refresh/",
                "method" : "POST", 
                "permission_classes": "AllowAny", 
                "description": "Get the new access/refresh token pair using a valid refresh token", 
                "body": "{refresh}", 
                "response": "{access, refresh}"}
    routes.append(api)

    # Read sample response from json file
    sample_response_file = open("base/api/.asset/documents.json", "r")
    sample_response = sample_response_file.read()
    sample_response_file.close()
    sample_response = json.loads(sample_response)

    api = {"route" : "/api/documents/",
                "method" : "GET", 
                "permission_classes": "IsAuthenticated", 
                "description": "Get all the documents of the current user", 
                "header": {"Content-Type": "application/json", "Authorization": "Bearer <token.access>"},
                "response": "[{id, file, uploaded_at, body, filename, author, created_at, last_modified, word_count, category, analysis_complete, user}]", 
                "sample_response": sample_response}
    routes.append(api)

    api = {"route" : "/api/upload/", 
                "method" : "POST", 
                "permission_classes": "IsAuthenticated", 
                "description": "Upload a document to the database as the current user",
                "header": {"Content-Type": "application/json", "Authorization": "Bearer <token.access>"}, 
                "body": "{file}",
                "response": {"file": "DIR_TO_FILE"}}
    routes.append(api)

    api = {"route" : "/api/registration/",
                "method" : "POST", 
                "permission_classes": "AllowAny", 
                "description": "Register a new user", 
                "body": "{username, email, first_name, last_name, password}}", 
                "response": "{username, email, first_name, last_name}"}
    routes.append(api)

    # Read sample response from json file
    sample_response_file = open("base/api/.asset/user.json", "r")
    sample_response = sample_response_file.read()
    sample_response_file.close()
    sample_response = json.loads(sample_response)
    api = {"route" : "/api/user/",
                "method" : "GET",
                "permission_classes": "IsAuthenticated",
                "description": "Get the current user's information",
                "header": {"Content-Type": "application/json", "Authorization": "Bearer <token.access>"}, 
                "response": "{id, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, groups, user_permissions, updating}", 
                "sample_response": sample_response}
    routes.append(api)

    api = {"route" : "/api/submit/",
                "method" : "GET",
                "permission_classes": "IsAuthenticated",
                "description": "Start the document analysis process for the current user",
                "header": {"Content-Type": "application/json", "Authorization": "Bearer <token.access>"}, 
                "response": "Document analysis complete"}
    routes.append(api)
    
    # Read sample response from json file
    sample_response_file = open("base/api/.asset/errors.json", "r")
    sample_response = sample_response_file.read()
    sample_response_file.close()
    sample_response = json.loads(sample_response)
    api = {"route" : "/api/errors/",
                "method" : "GET",
                "permission_classes": "IsAuthenticated",
                "description": "Get all the error stat of the current user",
                "header": {"Content-Type": "application/json", "Authorization": "Bearer <token.access>"}, 
                "response": "[{id, total_errors, all_errors, document}]", 
                "sample_response": sample_response}
    routes.append(api)

    # Read sample response from json file
    sample_response_file = open("base/api/.asset/error_details.json", "r")
    sample_response = sample_response_file.read()
    sample_response_file.close()
    sample_response = json.loads(sample_response)
    api = {"route" : "/api/errors/details",
                "method" : "GET",
                "permission_classes": "IsAuthenticated",
                "description": "Get all the error details of the current user",
                "header": {"Content-Type": "application/json", "Authorization": "Bearer <token.access>"}, 
                "response": "[{id, check_time, error_type, error_sub_type, error_msg, sentence, char_position_in_text_from, char_position_in_text_to, replacements, document}]",
                "sample_response": sample_response}
    routes.append(api)


    # routes = [
    #     "/api/", 
    #     "/api/token/",
    #     "/api/token/refresh/",
    #     "/api/documents/",
    #     "/api/upload/",
    #     "/api/registration/",
    #     "/api/user/",
    #     "/api/submit/",
    # ]

    return Response(routes)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDocuments(request):
    user = request.user
    # user = User.objects.get(id=1) # for debug purposes
    documents = user.document_set.all()
    serializer = DocumentSerializer(documents, many=True)

    # # Get sample response
    # serializer_data = serializer.data
    # # save to json file
    # path_file = "base\\api\\.asset\\documents.json"
    # with open(path_file, 'w') as outfile:
    #     json.dump(serializer_data, outfile)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    # user = User.objects.get(id=2) # for debug purposes
    serializer1 = UserSerializer(user)
    dict1 = serializer1.data
    try: 
        user_profile = user.userprofile
        serializer2 = UserProfilesSerializer(user_profile)
        dict2 = serializer2.data
        dict1.update(dict2)
    except Exception as e:
        print(e)
    
    # # Get sample response
    # serializer_data = dict1
    # # save to json file
    # path_file = "base\\api\\.asset\\user.json"
    # with open(path_file, 'w') as outfile:
    #     json.dump(serializer_data, outfile)
    return Response(dict1)

class UploadViewSet(ViewSet): 
    # View for uploading documents, only authenticated users can upload documents
    serializer_class = DocumentUploadSerializer 
    permission_classes = [IsAuthenticated] # Only authenticated users can upload documents

    def create(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid")
            serializer.preprocess(serializer.validated_data)

            user = request.user
            serializer.save(user=user)
            # serializer.save(user=User.objects.get(id=1)) # for debug purposes

            return Response(serializer.data)
        else: 
            return Response(serializer.errors)

class UserRegistrationView(CreateAPIView):
    model = get_user_model()
    permission_classes= [
        permissions.AllowAny
    ]
    serializer_class = RegisterSerializer 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def submitDocument(request):
    # when user hit submit button in HomePgae maybe updating
    # This will handle the document analysis 
    user = request.user
    # user = User.objects.get(id=1) # for debug purposes
    try:
        documents = user.document_set.all()
        for document in documents:
            if document.analysis_complete == False:
                getDocumentErrorDetail(document)
                document.analysis_complete = True
                document.save()

        return Response("Document analysis complete")
    except Exception as e:
        print(e)
        return Response("Error occured while analyzing document: " + str(e))


def getDocumentErrorDetail(document):
    # get all the error details of a document
    # create a DocumentErrorDetail object for each error
    language_tool = ErrorCheck(api_type='language_tool', language_longcode='en-AU')
    results = language_tool.check(document.body)
    for result in results:
        result.document = document
        result.save()
    generateDocumentErrorStat(results, document)



def generateDocumentErrorStat(results, document): 
    # generate the error statistics of a document
    # results is a list of DocumentErrorDetail objects
    # create a DocumentErrorStat object
    total_errors = len(results)
    stats = DocumentErrorStat(total_errors=total_errors, document=document)
    for result in results:
        error_type = result.error_type
        # print('error_type', error_type)
        all_errors = stats.all_errors
        if error_type in all_errors:
            all_errors[error_type] += 1
        else:
            all_errors[error_type] = 1
    stats.all_errors = all_errors
    stats.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getErrors(request):
    # get all the errors of the current user
    user = request.user
    # user = User.objects.get(id=1) # for debug purposes
    documents = user.document_set.all()
    errors = []
    for doc in documents:
        if doc.analysis_complete == True:
            error_stat = DocumentErrorStat.objects.get(document=doc)
            errors.append(error_stat)
    serializer = DocumentErrorStatSerializer(errors, many=True)

    # # Get sample response
    # serializer_data = serializer.data
    # # save to json file
    # path_file = "base\\api\\.asset\\errors.json"
    # with open(path_file, 'w') as outfile:
    #     json.dump(serializer_data, outfile)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getErrorDetails(request):
    # get all error details of the current user
    user = request.user
    # user = User.objects.get(id=1) # for debug purposes
    documents = user.document_set.all()
    errors = []
    for doc in documents:
        if doc.analysis_complete == True:
            error_details = DocumentErrorDetail.objects.filter(document=doc)
            # loop through all the error details of a document
            for error_detail in error_details:
                errors.append(error_detail)
    serializer = DocumentErrorDetailSerializer(errors, many=True)
    serializer_data = serializer.data

    # # Get sample response
    # serializer_data = serializer.data
    # # save to json file
    # path_file = "base\\api\\.asset\\error_details.json"
    # with open(path_file, 'w') as outfile:
    #     json.dump(serializer_data, outfile)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getChartInfo(request): 
    # get the chart info of the current user
    user = request.user
    # user = User.objects.get(id=1) # for debug purposes
    documents = user.document_set.all()
    errors = []
    timestamps = []
    chart_info = []
    for doc in documents:
        if doc.analysis_complete == True:
            error_stat = DocumentErrorStat.objects.get(document=doc)
            timestamp = error_stat.document.last_modified
            timestamp = timestamp.strftime("%Y-%m")
            error_stat.timestamp = timestamp
            if timestamp not in timestamps:
                timestamps.append(timestamp)
            # print(error_stat.timestamp)
            errors.append(error_stat)

    print(timestamps)
    for timestamp in timestamps:
        total_errors = 0
        all_errors = {}
        for error in errors:
            if error.timestamp == timestamp:
                total_errors += error.total_errors
                for key in error.all_errors:
                    if key in all_errors:
                        all_errors[key] += error.all_errors[key]
                    else:
                        all_errors[key] = error.all_errors[key]
        chart_info.append({"timestamp": timestamp, "total_errors": total_errors, "all_errors": all_errors})

    return Response(chart_info)

