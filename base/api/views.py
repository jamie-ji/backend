from rest_framework.viewsets import ViewSet
from rest_framework.response import Response 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from base.models import Document, DocumentErrorDetail, DocumentErrorStat
from .serializers import DocumentSerializer, DocumentUploadSerializer, RegisterSerializer
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
    routes = [
        "/api/", 
        "/api/token/",
        "/api/token/refresh/",
        "/api/documents/",
        "/api/upload/",
        "/api/registration/",
        "/api/register/",
        "/api/user/",
        "/api/submit/",
    ]

    return Response(routes)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDocuments(request):
    user = request.user
    # user = User.objects.get(id=1) # for debug purposes
    documents = user.document_set.all()
    serializer = DocumentSerializer(documents, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def current_user(request):
    user = User.objects.get(id=1) # for debug purposes
    return Response({
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    })

class UploadViewSet(ViewSet): 
    # View for uploading documents, only authenticated users can upload documents
    # TODO: The authentication is not implemented for debug purposes, you can uncomment the permission_classes line to enable authentication
    serializer_class = DocumentUploadSerializer 
    # permission_classes = [IsAuthenticated] # Only authenticated users can upload documents

    def create(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid")
            serializer.preprocess(serializer.validated_data)

            # serializer.save(user=request.user)
            serializer.save(user=User.objects.get(id=1)) # for debug purposes

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
# @permission_classes([IsAuthenticated])
def submitDocument(request):
    # when user hit submit button in HomePgae maybe
    # This will handle the document analysis 
    # user = request.user
    try:
        user = User.objects.get(id=1) # for debug purposes
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
        print('error_type', error_type)
        all_errors = stats.all_errors
        if error_type in all_errors:
            all_errors[error_type] += 1
        else:
            all_errors[error_type] = 1
    stats.all_errors = all_errors
    stats.save()