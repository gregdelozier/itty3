import io
import unittest

import itty3


class TestHttpRequest(unittest.TestCase):
    def setUp(self):
        self.request = itty3.HttpRequest(
            "/greet/person/?name=Daniel#visited", itty3.GET
        )

    def test_attributes_simple(self):
        self.assertEqual(self.request.method, "GET")
        self.assertEqual(self.request.body, "")
        self.assertEqual(self.request.scheme, "http")
        self.assertEqual(self.request.host, "")
        self.assertEqual(self.request.port, 80)
        self.assertEqual(self.request.path, "/greet/person/")
        self.assertEqual(self.request.query["name"], ["Daniel"])
        self.assertEqual(self.request.fragment, "visited")

    def test_attributes_complex(self):
        req = itty3.HttpRequest(
            "https://example.com:443/greet/person/?name=Daniel#visited",
            itty3.PATCH,
            body='{"hello": "world"}',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            scheme="https",
            host="example.com",
            port=443,
        )

        self.assertEqual(req.method, "PATCH")
        self.assertEqual(req.body, '{"hello": "world"}')
        self.assertEqual(req.scheme, "https")
        self.assertEqual(req.host, "example.com")
        self.assertEqual(req.port, 443)
        self.assertEqual(req.path, "/greet/person/")
        self.assertEqual(req.query["name"], ["Daniel"])
        self.assertEqual(req.fragment, "visited")

    def test_split_uri(self):
        bits = self.request.split_uri(
            "https://foo.com:8080/this/is/a/crazy/path?name=Joe"
        )
        self.assertEqual(
            bits,
            {
                "fragment": "",
                "path": "/this/is/a/crazy/path",
                "query": {"name": ["Joe"]},
                "netloc": "foo.com:8080",
            },
        )

    def test_from_wsgi(self):
        mock_environ = {
            "HTTP_CONTENT-TYPE": "application/json",
            "HTTP_ACCEPT": "application/json",
            "REQUEST_METHOD": "POST",
            "wsgi.input": io.StringIO('{"hello": "world"}'),
            "wsgi.url_scheme": "https",
            "HTTPS": "on",
            "HTTP_HOST": "example.com",
            "SERVER_PORT": "443",
            "PATH_INFO": "/secure/checkout",
            "CONTENT_LENGTH": 18,
        }

        req = itty3.HttpRequest.from_wsgi(mock_environ)
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.body, '{"hello": "world"}')
        self.assertEqual(req.scheme, "https")
        self.assertEqual(req.host, "example.com")
        self.assertEqual(req.port, 443)
        self.assertEqual(req.path, "/secure/checkout")
        self.assertEqual(len(req.query), 0)
        self.assertEqual(req.fragment, "")

    def test_content_type_simple(self):
        self.assertEqual(self.request.content_type(), "text/html")

    def test_content_type_complex(self):
        req = itty3.HttpRequest(
            "https://example.com:443/greet/person/?name=Daniel#visited",
            itty3.PATCH,
            body='{"hello": "world"}',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            scheme="https",
            host="example.com",
            port=443,
        )
        self.assertEqual(req.content_type(), "application/json")

    def test_GET(self):
        self.assertEqual(self.request.GET["name"], "Daniel")

    def test_POST(self):
        req = itty3.HttpRequest(
            "/", itty3.POST, body="name=Daniel&msg=Hello&submit=true"
        )
        self.assertEqual(req.POST["name"], "Daniel")
        self.assertEqual(req.POST["msg"], "Hello")
        self.assertEqual(req.POST["submit"], "true")

    def test_PUT(self):
        req = itty3.HttpRequest(
            "/", itty3.PUT, body="name=Daniel&msg=Hello&submit=true"
        )
        self.assertEqual(req.PUT["name"], "Daniel")
        self.assertEqual(req.PUT["msg"], "Hello")
        self.assertEqual(req.PUT["submit"], "true")

    def test_is_ajax(self):
        self.assertFalse(self.request.is_ajax())

        self.request.headers["X-Requested-With"] = "XMLHttpRequest"
        self.assertTrue(self.request.is_ajax())

    def test_is_secure(self):
        self.assertFalse(self.request.is_secure())

        self.request.scheme = "https"
        self.assertTrue(self.request.is_secure())

    def test_json(self):
        req = itty3.HttpRequest(
            "/greet/",
            itty3.POST,
            body='{"hello": "world"}',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        self.assertEqual(req.json(), {"hello": "world"})
