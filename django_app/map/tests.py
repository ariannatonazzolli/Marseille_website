from django.test import SimpleTestCase


class GoogleVerificationViewTests(SimpleTestCase):
    def test_google_verification_file_is_served(self):
        response = self.client.get("/googlec2b4a3ec3165f0c3.html")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"].startswith("text/html"), True)
