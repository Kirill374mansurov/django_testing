import pytest

from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from random import choice

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


COMMENT_FORM = {'text': 'Текст'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, client, detail_url):
    old_count_comment = Comment.objects.count()
    client.post(detail_url, data=COMMENT_FORM)
    comments_count = Comment.objects.count()
    assert comments_count == old_count_comment


@pytest.mark.django_db
def test_user_can_create_comment(news, author_client, author, detail_url):
    Comment.objects.all().delete()
    old_count_comment = Comment.objects.count()
    response = author_client.post(detail_url, data=COMMENT_FORM)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == old_count_comment + 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_FORM['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, detail_url):
    old_count_comment = Comment.objects.count()
    bad_words_data = {
        'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    }
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == old_count_comment


def test_author_can_delete_comment(
        author_client, comment, news, detail_url, delete_url
):
    old_count_comment = Comment.objects.count()
    response = author_client.delete(delete_url)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == old_count_comment - 1


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment, delete_url
):
    old_count_comment = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == old_count_comment


FORM_DATA = {'text': 'Новый комент'}


def test_author_can_edit_comment(
        author_client, author, comment, news, detail_url, edit_url
):
    response = author_client.post(edit_url, data=FORM_DATA)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, edit_url
):
    old_text = comment.text
    response = not_author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    refresh_comment = Comment.objects.get(id=comment.id)
    assert refresh_comment.text == old_text
