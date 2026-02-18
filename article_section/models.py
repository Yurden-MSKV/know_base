import re

from django.contrib.auth.models import Group
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class Section(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название')
    allowed_groups = models.ManyToManyField(Group,
                                            verbose_name='Группы с доступом',
                                            blank=True)

    class Meta:
        verbose_name = 'Разделы'
        verbose_name_plural = 'Разделы'
        permissions = [
            ('view_engineering_section', 'Может видеть инженерные разделы'),
            ('view_sales_section', 'Может видеть разделы продаж'),
        ]

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=150,
                             verbose_name='Название')
    section = models.ForeignKey(Section,
                                on_delete=models.CASCADE,
                                related_name='articles',
                                verbose_name='Раздел',
                                null=True,
                                blank=True)
    content = CKEditor5Field('Text',
                             config_name='extends',
                             default='')

    class Meta:
        verbose_name = 'Статьи'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title

    def get_short_content(self, max_length=100):
        """
        Возвращает укороченное содержимое без изображений и с заменой &nbsp; на пробелы
        """
        # Удаляем все теги img
        content_no_images = re.sub(r'<img[^>]*>', '', self.content)

        # Заменяем &nbsp; на обычные пробелы
        content_no_nbsp = re.sub(r'&nbsp;', ' ', content_no_images)

        # Получаем чистый текст
        text_only = re.sub(r'<[^>]*>', '', content_no_nbsp)

        # Обрезаем текст
        if len(text_only) > max_length:
            return text_only[:max_length] + '...'
        return text_only

    def get_short_content_safe(self, max_length=100):
        """
        Безопасная версия для использования в шаблонах
        """
        from django.utils.safestring import mark_safe
        return mark_safe(self.get_short_content(max_length))