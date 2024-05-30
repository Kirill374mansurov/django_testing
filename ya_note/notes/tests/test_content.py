from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestListNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_list = reverse('notes:list')
        cls.author_create = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note_one = Note.objects.create(
            title='Заметка1',
            text='Текст1',
            slug='adress_one',
            author=cls.author_create
        )
        cls.note_two = Note.objects.create(
            title='Заметка2',
            text='Текст2',
            slug='adress_two',
            author=cls.reader
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author_create)

    def test_list_content_author(self):
        response = self.author_client.get(self.url_list)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note_one, response.context['object_list'])

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note_one.slug,))
        )
        for name, args in urls:
            with self.subTest(user=self.author_create, name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author_create)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
