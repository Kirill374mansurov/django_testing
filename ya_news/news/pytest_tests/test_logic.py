import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, comment_form, client):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=comment_form)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(news, comment_form, author_client):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=comment_form)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form['text']
    assert comment.news == comment_form['news']
    assert comment.author == comment_form['author']


def test_user_cant_use_bad_words(author_client, news, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment, news, detail_url):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


FORM_DATA = {'text': 'Новый комент'}


def test_author_can_edit_comment(author_client, comment, news, detail_url):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=FORM_DATA)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    old_text = comment.text
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
