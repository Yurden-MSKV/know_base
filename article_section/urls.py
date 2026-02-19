from django.urls import path
from article_section import views as article_views

urlpatterns = [
    path('', article_views.main_page, name='main_page'),
    path('search/', article_views.filter_search, name='filtered_search'),
    path('article/<int:article_id>/', article_views.article_page, name='article_page'),
    path('article/<int:article_id>/edit/', article_views.article_edit, name='article_edit'),
    path('section/<int:section_id>/create_article/', article_views.article_create, name='article_create'),
    path('section/<int:section_id>/save_article/', article_views.article_create_save, name='article_create_save'),
    # path('section/<int:section_id>/', article_views.section_page, name='section_page'),
]