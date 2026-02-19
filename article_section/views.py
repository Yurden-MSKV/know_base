from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from article_section.forms import ArticleForm
from article_section.models import Article, Section


def index(request):
    return redirect('home')


def main_page(request):
    article_id = request.GET.get('article_id')
    article = None
    if article_id:
        article = get_object_or_404(Article, id=article_id)

    user_group = request.user.groups.all()
    print(user_group)

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

def article_page(request, article_id):
    if not request.headers.get('HX-Request'):
        # Перенаправляем на главную с ID статьи
        return redirect(f"{reverse('main_page')}?article_id={article_id}")

    article = Article.objects.get(id=article_id)
    print(article.title)

    context = {
        'article': article,
    }

    return render(request, 'partials/article_block.html', context)

def article_edit(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    # TODO: сделать проверку группы юзера?
    if request.method == 'POST':
        print("POST data:", request.POST)  # Посмотрите, что приходит
        print("Content:", request.POST.get('content'))
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.save()

            context = {
                'article': article,
            }
            return render(request, 'partials/article_block.html', context)
        return None

    else:
        form = ArticleForm(instance=article)
        return render(request, 'partials/article_edit.html', {
            'form': form,
            'article': article,})


def article_create(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    form = ArticleForm()

    return render(request, 'partials/article_edit.html', {
        'form': form,
        'section': section,
        'is_creating': True,  # Флаг для режима создания
    })


def article_create_save(request, section_id):
    print(f"💾 Сохранение новой статьи в разделе {section_id}")

    if request.method == 'POST':
        section = get_object_or_404(Section, id=section_id)
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.section = section
            article.save()

            print(f"✅ Статья создана: {article.title}")
            # Возвращаем страницу со статьей
            return render(request, 'partials/article_block.html', {'article': article})
        else:
            print(f"❌ Ошибки в форме: {form.errors}")
            # Если форма не валидна, возвращаем форму с ошибками
            return render(request, 'partials/article_edit.html', {
                'form': form,
                'section': section,
                'is_creating': True
            })

    return redirect('section_page', section_id=section_id)