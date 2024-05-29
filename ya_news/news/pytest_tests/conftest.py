import pytest
from django.test.client import Client
from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def news_max():
    today = datetime.today()
    all_news = [
        News.objects.create(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return all_news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий'
    )
    return comment


@pytest.fixture
def comment_max(news, author):
    now = timezone.now()
    all_comment = [
        Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
            created=now + timedelta(days=index)
        )
        for index in range(10)
    ]
    return all_comment


@pytest.fixture
def comment_form(news, author):
    return {
        'news': news,
        'author': author,
        'text': 'Текст'
    }


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))
