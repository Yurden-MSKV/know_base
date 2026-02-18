from django.contrib import admin

from article_section.models import Article, Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['allowed_groups']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'content']