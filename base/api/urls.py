from django.urls import path, include
from . import views
from .views import MyTokenObtainPairView
from .views import UserRegistrationView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("",  views.getRoutes, name="routes"),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("documents/", views.getDocuments, name="documents"),
    path("upload/", views.UploadViewSet.as_view({'post': 'create'}), name="upload"),
    path("registration/",views.UserRegistrationView.as_view(),name='registration'), 
    path('validate/', views.validate_code, name='validate_code'),
    path("submit/", views.submitDocument, name="submit"),
    path("user/",views.current_user,name="user"), 
    path("errors/", views.getErrors, name="errors"),
    path("errors/details", views.getErrorDetails, name="error_details"),
    path("errors/chart", views.getChartInfo, name="error_chart"),
]