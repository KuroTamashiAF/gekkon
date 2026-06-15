"""
URL configuration for HenkonKnowledgeTest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from main.views import custom_404, custom_403, custom_500, custom_400

handler400 = custom_400
handler403 = custom_403
handler404 = custom_404
handler500 = custom_500


urlpatterns = [
    path("verwalter/", admin.site.urls),
    path("", include("main.urls", namespace="main")),
    path("", include("gtests.urls", namespace="gtests")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
