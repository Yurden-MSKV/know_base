from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']  # Поля, которые будут в форме
        widgets = {
            # Указываем, что поле content должно использовать редактор
            'content': CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, # Важно для работы JS
                config_name='extends' # Имя конфига из вашего settings.py
            )
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержимое статьи',
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        print(f"clean_content: {content}")  # Что видит форма?
        return content