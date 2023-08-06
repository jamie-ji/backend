from rest_framework.viewsets import ViewSet
from rest_framework.response import Response 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from base.models import Document
from .serializers import DocumentSerializer

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
    ]

    return Response(routes)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDocuments(request):
    user = request.user
    documents = user.document_set.all()
    serializer = DocumentSerializer(documents, many=True)
    return Response(serializer.data)


class UploadViewSet(ViewSet): 
    # View for uploading documents, only authenticated users can upload documents
    # TODO: The authentication is not implemented for debug purposes, you can uncomment the permission_classes line to enable authentication
    serializer_class = DocumentSerializer 
    # permission_classes = [IsAuthenticated] # Only authenticated users can upload documents

    def create(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid")
            serializer.preprocess(serializer.validated_data)

            # serializer.save(user=request.user)
            serializer.save(user=User.objects.get(id=1)) # for debug purposes

            return Response(serializer.data)
        else: 
            return Response(serializer.errors)