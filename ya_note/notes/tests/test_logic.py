from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify
from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Человек')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.TEXT = 'Текст1'
        cls.TITLE = 'Заметка1'
        cls.SLUG = 'adress'
        cls.form_note = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
            'author': cls.user
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, self.form_note)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, self.form_note)
        self.assertRedirects(response, '/done/')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):

    TEXT = 'Текст'
    NEW_TEXT = 'Текст новый'
    TITLE = 'Заметка'
    SLUG = 'adress'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Другой автор')
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author
        )
        cls.done = reverse('notes:success')
        cls.url = reverse('notes:add')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse(
            'notes:delete', args=(cls.note.slug,)
        )
        cls.form_note = {
            'title': cls.TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.SLUG
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, self.form_note)
        self.assertRedirects(response, self.done)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.not_author_client.post(self.edit_url, self.form_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.TEXT)

    def test_create_not_unique_slug(self):
        new_note = self.form_note
        new_note['author'] = self.author
        response = self.author_client.post(self.url, new_note)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG + WARNING
        )

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_note.pop('slug')
        self.note.delete()
        response = self.author_client.post(url, data=self.form_note)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_note['title'])
        self.assertEqual(new_note.slug, expected_slug)
