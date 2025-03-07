import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(news_max, client, home_url):
    response = client.get(home_url)
    all_news = response.context['object_list']
    news_count = all_news.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in all_news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(comment_max, news, client, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news_cont = response.context['news']
    all_comments = news_cont.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(news, client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(news, author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
