from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Какой-то чел')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Какой-то текст',
            slug='adress',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.url_home = reverse('notes:home')
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_signup = reverse('users:signup')
        cls.url_list = reverse('notes:list')
        cls.url_success = reverse('notes:success')
        cls.url_edit = reverse(
            'notes:edit', args=(cls.note.slug,)
        )
        cls.url_delete = reverse(
            'notes:delete', args=(cls.note.slug,)
        )
        cls.url_detail = reverse(
            'notes:detail', args=(cls.note.slug,)
        )
        cls.url_add = reverse('notes:add')

    def test_anonymous_client(self):
        urls = (
            self.url_home,
            self.url_login,
            self.url_logout,
            self.url_signup,
        )
        for url in urls:
            with self.subTest():
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        urls = (
            self.url_success,
            self.url_list,
            self.url_home,
            self.url_login,
            self.url_logout,
            self.url_signup,
        )
        for url in urls:
            with self.subTest():
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_and_delete(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user_client, status in users_statuses:
            for url in (self.url_edit, self.url_delete, self.url_detail):
                with self.subTest():
                    response = user_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.url_list,
            self.url_add,
            self.url_success,
            self.url_edit,
            self.url_delete,
            self.url_detail
        )
        for url in urls:
            with self.subTest():
                redirect_url = f'{self.url_login}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
