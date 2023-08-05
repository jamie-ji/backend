from rest_framework.response import Response 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from base.models import Document
from .serializers import DocumentSerializer

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

class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def getRoutes(request): 
    routes = [
        "/api/", 
        "/api/token/",
        "/api/token/refresh/",
    ]

    return Response(routes)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDocuments(request):
    user = request.user
    # documents = Document.objects.filter(user=user)
    documents = user.document_set.all()
    serializer = DocumentSerializer(documents, many=True)
    return Response(serializer.data)