from django.test import TestCase
from django.urls import reverse


class LiveClassesViewTests(TestCase):
    def test_live_classes_page_returns_200(self):
        response = self.client.get(reverse('live_classes'))
        self.assertEqual(response.status_code, 200)
