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
        "/api/registeration/",

        "/api/submit/",
    ]

    return Response(routes)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def getDocuments(request):
    # user = request.user
    user = User.objects.get(id=1) # for debug purposes
    documents = user.document_set.all()
    serializer = DocumentSerializer(documents, many=True)
    return Response(serializer.data)


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


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def submitDocument(request):
    # when user hit submit button in HomePgae maybe
    # This will handle the document analysis 
    pass