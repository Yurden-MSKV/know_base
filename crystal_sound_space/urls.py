from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from article_section import views as article_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('article_section.urls')),
]

urlpatterns += [
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
