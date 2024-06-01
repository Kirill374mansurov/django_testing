from http import HTTPStatus

from django.contrib.auth import get_user_model, get_user
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


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
        }
        cls.success_url = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        old_notes_count = Note.objects.count()
        self.client.post(self.url, self.form_note)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, old_notes_count)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        old_notes_count = Note.objects.count()
        response = self.auth_client.post(self.url, self.form_note)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, old_notes_count + 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_note['text'])
        self.assertEqual(note.title, self.form_note['title'])
        self.assertEqual(note.slug, self.form_note['slug'])
        self.assertEqual(note.author, get_user(self.auth_client))


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
        cls.add_url = reverse('notes:add')
        cls.form_note = {
            'title': cls.TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.SLUG
        }

    def test_author_can_delete_note(self):
        old_notes_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, old_notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        old_notes_count = Note.objects.count()
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, old_notes_count)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, self.form_note)
        self.assertRedirects(response, self.done)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_note['text'])
        self.assertEqual(self.note.slug, self.form_note['slug'])
        self.assertEqual(self.note.title, self.form_note['title'])
        self.assertEqual(self.note.author, get_user(self.author_client))

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.not_author_client.post(self.edit_url, self.form_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        refresh_note = Note.objects.get(id=self.note.id)
        self.assertEqual(refresh_note.text, self.note.text)
        self.assertEqual(refresh_note.title, self.note.title)
        self.assertEqual(refresh_note.slug, self.note.slug)
        self.assertEqual(refresh_note.author, self.note.author)

    def test_create_not_unique_slug(self):
        response = self.author_client.post(self.url, self.form_note)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG + WARNING
        )

    def test_empty_slug(self):
        self.form_note.pop('slug')
        Note.objects.all().delete()
        old_count = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_note)
        self.assertRedirects(response, self.done)
        self.assertEqual(Note.objects.count(), old_count + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_note['title'])
        self.assertEqual(new_note.slug, expected_slug)
