from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.views.generic import RedirectView
from rest_framework.authtoken.views import obtain_auth_token
from api.views import CustomObtainAuthToken

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('auth/', CustomObtainAuthToken.as_view()),
]