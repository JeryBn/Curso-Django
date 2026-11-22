from django.test import SimpleTestCase


class CorsTests(SimpleTestCase):
    def test_allows_react_preflight_with_authorization(self):
        response = self.client.options(
            "/api/exams/",
            headers={
                "origin": "http://localhost:5173",
                "access-control-request-method": "DELETE",
                "access-control-request-headers": "authorization",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Access-Control-Allow-Origin"], "http://localhost:5173"
        )
        self.assertIn("authorization", response["Access-Control-Allow-Headers"])

    def test_omits_cors_header_for_another_origin(self):
        response = self.client.options(
            "/api/exams/",
            headers={
                "origin": "http://127.0.0.1:5173",
                "access-control-request-method": "GET",
            },
        )
        self.assertNotIn("Access-Control-Allow-Origin", response)

