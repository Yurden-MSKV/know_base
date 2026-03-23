from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q

from article_section.forms import ArticleForm, ArticleNewForm
from article_section.models import Article, Section, ArticleVersion

def main_page(request):
    article_id = request.GET.get('article_id')
    article = None
    if article_id:
        article = get_object_or_404(Article, id=article_id)

    user_group = request.user.groups.all()

    user_sections = Section.objects.filter(allowed_groups__in=user_group).prefetch_related('articles')

    context = {
        'user_sections': user_sections,
        'article': article,
    }

    response = render(request, 'main_page.html', context)

    if article and not request.headers.get('HX-Request'):
        response['HX-Push-Url'] = '/'

    return response

    return render(request, 'main_page.html', context)


def filter_search(request):
    query = request.GET.get('search', '').strip()

    if query:
        # Используем Q объекты для поиска по разным вариантам регистра
        q_objects = Q()
        for variant in [query, query.lower(), query.upper(), query.capitalize()]:
            q_objects |= Q(title__icontains=variant)

        articles = Article.objects.filter(q_objects).distinct().select_related('section')

        sections_dict = {}
        for article in articles:
            section = article.section
            if section not in sections_dict:
                sections_dict[section] = []
            sections_dict[section].append(article)

        results = [
            {'section': section, 'articles': arts}
            for section, arts in sections_dict.items()
        ]
    else:
        sections = Section.objects.all().prefetch_related('articles')
        results = [
            {'section': section, 'articles': section.articles.all()}
            for section in sections
        ]

    return render(request, 'partials/filtered_search.html', {
        'results': results,
        'query': query
    })

@login_required
def article_page(request, article_id):

    article = Article.objects.get(id=article_id)
    user_group = request.user.groups.all()
    user_sections = Section.objects.filter(allowed_groups__in=user_group)
    if article.section in user_sections:
        if not request.headers.get('HX-Request'):
            # Перенаправляем на главную с ID статьи
            return redirect(f"{reverse('main_page')}?article_id={article_id}")
        # TODO: проверка доступа к разделу
        version = get_object_or_404(ArticleVersion, article=article_id,
                                    is_current_version=True)

        context = {
            'version': version,
            'article': version.article,
        }

        return render(request, 'partials/article_block.html', context)
    else:
        print(f'У юзера {request.user.username} нет доступа к разделу.')
        return redirect(f"{reverse('main_page')}")


def article_edit(request, article_id):
    article = Article.objects.get(id=article_id)
    user_group = request.user.groups.all()
    user_sections = Section.objects.filter(allowed_groups__in=user_group)
    if article.section in user_sections:
        current_version = get_object_or_404(
            ArticleVersion.objects.select_related('article'),
            article=article_id,
            is_current_version=True
        )

        if request.method == 'POST':
            form = ArticleForm(request.POST, instance=current_version)
            if form.is_valid():
                new_content = form.cleaned_data['content']
                last_version_number = ArticleVersion.objects.select_related('article').values_list('version_number', flat=True).last()
                new_number = str(int(last_version_number) + 1).zfill(3)

                ArticleVersion.objects.create(
                    author=request.user,
                    article=current_version.article,
                    version_number=new_number,
                    content=new_content,
                )

                success_message = "Правка отправлена на проверку."
                context = {
                    'version': current_version,
                    'article': current_version.article,
                    'message': success_message
                }
                return render(request, 'partials/article_block.html', context)
            else:
                # Если форма не валидна, показываем ошибки
                context = {
                    'form': form,
                    'version': current_version,
                    'article': current_version.article,
                    'errors': form.errors
                }
                return render(request, 'partials/article_edit.html', context)

        else:
            form = ArticleForm(instance=current_version)
            context = {
                'form': form,
                'version': current_version,
                'article': current_version.article,
            }
            return render(request, 'partials/article_edit.html', context)
    else:
        print(f'У юзера {request.user.username} нет доступа к разделу.')
        return redirect(f"{reverse('main_page')}")

#
#
# def article_create(request, section_id):
#     section = get_object_or_404(Section, id=section_id)
#     form = ArticleForm()
#
#     return render(request, 'partials/article_edit.html', {
#         'form': form,
#         'section': section,
#         'is_creating': True,  # Флаг для режима создания
#     })
#
#
@login_required
def article_create(request, section_id):
    section = Section.objects.get(id=section_id)
    print(section)
    user = request.user
    print(user)
    user_group = user.groups.all()
    print(user_group)
    user_sections = Section.objects.filter(allowed_groups__in=user_group)
    print(user_sections)
    # NOTE: Эту проверку нужно протестировать!
    if section in user_sections:
        print('Да')
        if request.method == 'POST':
            form = ArticleNewForm(request.POST)
            if form.is_valid():
                user_action = 'create'
                article, version = form.save(user_action, section, user)
                return render(request, 'partials/article_block.html', {'article': article, 'version': version})
            else:
                return HttpResponse('Не получилось.')
        else:
            form = ArticleNewForm()
            return render(request, 'partials/article_edit.html', {'form': form})
    else:
        print('Нет прав на создание статьи в этом разделе.')
        return redirect(f"{reverse('main_page')}")



# def article_create(request, section_id):
#     print(f"💾 Сохранение новой статьи в разделе {section_id}")
#
#     if request.method == 'POST':
#         section = get_object_or_404(Section, id=section_id)
#         form = ArticleForm(request.POST)
#
#         if form.is_valid():
#             article = form.save(commit=False)
#             article.section = section
#             article.save()
#
#             print(f"✅ Статья создана: {article.title}")
#             # Возвращаем страницу со статьей
#             return render(request, 'partials/article_block.html', {'article': article})
#         else:
#             print(f"❌ Ошибки в форме: {form.errors}")
#             # Если форма не валидна, возвращаем форму с ошибками
#             return render(request, 'partials/article_edit.html', {
#                 'form': form,
#                 'section': section,
#                 'is_creating': True
#             })
#
#     return redirect('section_page', section_id=section_id)
