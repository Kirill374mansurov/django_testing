from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestListNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_list = reverse('notes:list')
        cls.author_one = User.objects.create(username='Автор один')
        cls.author_two = User.objects.create(username='Автор два')
        cls.note_one = Note.objects.create(
            title='Заметка1',
            text='Текст1',
            slug='adress_one',
            author=cls.author_one
        )
        cls.note_two = Note.objects.create(
            title='Заметка2',
            text='Текст2',
            slug='adress_two',
            author=cls.author_two
        )

    def test_list_content_author(self):
        self.client.force_login(self.author_one)
        response = self.client.get(self.url_list)
        self.assertIn('object_list', response.context)
        for note in response.context['object_list']:
            self.assertEqual(
                response.context['user'], note.author
            )

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note_one.slug,))
        )
        for name, args in urls:
            with self.subTest(user=self.author_one, name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author_one)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
