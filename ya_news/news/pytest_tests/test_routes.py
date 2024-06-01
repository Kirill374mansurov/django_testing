from http import HTTPStatus as ht

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (
            lf('home_url'),
            lf('client'),
            ht.OK
        ),
        (
            lf('login_url'),
            lf('client'),
            ht.OK
        ),
        (
            lf('logout_url'),
            lf('client'),
            ht.OK
        ),
        (
            lf('signup_url'),
            lf('client'),
            ht.OK
        ),
        (
            lf('edit_url'),
            lf('author_client'),
            ht.OK
        ),
        (
            lf('edit_url'),
            lf('not_author_client'),
            ht.NOT_FOUND
        ),
        (
            lf('delete_url'),
            lf('author_client'),
            ht.OK
        ),
        (
            lf('delete_url'),
            lf('not_author_client'),
            ht.NOT_FOUND
        ),
        (
            lf('detail_url'),
            lf('client'),
            ht.OK
        ),
    ),
)
def test_pages_availability(reverse_url, parametrized_client, status):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    ),
)
def test_redirect_for_anonymous_client(
        client, reverse_url, comment, login_url
):
    expected_url = f'{login_url}?next={reverse_url}'
    response = client.get(reverse_url)
    assertRedirects(response, expected_url)
