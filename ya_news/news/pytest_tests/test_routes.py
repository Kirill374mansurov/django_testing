import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (
            pytest.lazy_fixture('home_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('login_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('logout_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('signup_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('detail_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
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
