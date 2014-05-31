#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from nose.tools import *  # PEP8 asserts

from webtest.app import AppError

from .testapp import app
from webtest_plus import TestApp


class TestTestApp(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(app)
        self.auth = ("admin", "secret")

    def test_auth_get(self):
        res = self.app.get("/foo/bar/", auth=self.auth)
        assert_equal(res.status_code, 200)

    def test_bad_auth_get(self):
        # /foo/bar/ requires HTTP basic auth
        res = self.app.get("/foo/bar/", expect_errors=True)
        assert_equal(res.status_code, 401)
        bad_auth = ("no", "go")
        res = self.app.get("/foo/bar/", auth=bad_auth, expect_errors=True)
        assert_equal(res.status_code, 401)

    def test_auth_post(self):
        res = self.app.post("/foo/bar/baz/", auth=self.auth)
        assert_equal(res.status_code, 200)

    def test_auto_follow(self):
        res = self.app.get("/redirect/", auto_follow=True)
        assert_equal(res.status_code, 200)

    def test_authorize(self):
        self.app.authenticate(username='admin', password='secret')
        res = self.app.get("/foo/bar/")
        assert_equal(res.status_code, 200)
        self.app.deauthenticate()
        res = self.app.get("/foo/bar/", expect_errors=True)
        assert_equal(res.status_code, 401)

    def test_auth_put(self):
        assert_equal(self.app.put("/foo/bar/baz/", expect_errors=True).status_code,
                    401)
        assert_equal(self.app.put("/foo/bar/baz/", auth=self.auth).status_code, 200)

    def test_auth_patch(self):
        assert_equal(self.app.patch("/foo/bar/baz/", expect_errors=True).status_code,
                    401)
        assert_equal(self.app.patch("/foo/bar/baz/", auth=self.auth).status_code, 200)

    def test_auth_options(self):
        assert_equal(self.app.options("/foo/bar/baz/", expect_errors=True).status_code,
                    401)
        assert_equal(self.app.options("/foo/bar/baz/", auth=self.auth).status_code, 200)

    def test_auth_delete(self):
        assert_equal(self.app.delete("/foo/bar/baz/", expect_errors=True).status_code,
                    401)
        assert_equal(self.app.delete("/foo/bar/baz/", auth=self.auth).status_code, 200)

    def test_auth_post_json(self):
        assert_equal(self.app.post_json("/secretjson/", {"name": "Steve"},
                    expect_errors=True).status_code, 401)
        res = self.app.post_json("/secretjson/", {"name": "Steve"}, auth=self.auth)
        assert_equal(res.request.content_type, "application/json")
        assert_equal(res.status_code, 200)

    def test_click_with_auth(self):
        res = self.app.get("/")
        assert_raises(AppError, lambda: res.click("Bar"))
        res = self.app.get("/")
        res = res.click("Bar", auth=self.auth)
        assert_equal(res.status_code, 200)

    def test_click_with_authenticate(self):
        self.app.authenticate(username=self.auth[0], password=self.auth[1])
        res = self.app.get('/')
        res = res.click("Bar")
        assert_equal(res.status_code, 200)

    def test_clickbutton_with_auth(self):
        res = self.app.get("/")
        assert_raises(AppError, lambda: res.clickbutton("Click me"))
        res = self.app.get('/')
        res = res.clickbutton("Click me", auth=self.auth)

    def test_clickbutton_with_authenticate(self):
        self.app.authenticate(username=self.auth[0], password=self.auth[1])
        res = self.app.get('/')
        res = res.clickbutton("Click me")
        assert_equal(res.status_code, 200)
        assert_equal(res.request.path, "/foo/bar/")

    def test_auth_with_token(self):
        assert_equal(self.app.post('/requires_token', expect_errors=True).status_code, 401)
        res = self.app.post('/requires_token', auth='mytoken', auth_type='jwt')
        assert_equal(res.status_code, 200)

    def test_authenticate_with_token(self):
        self.app.authenticate_with_token('mytoken')
        res = self.app.post('/requires_token')
        assert_equal(res.status_code, 200)

        self.app.deauthenticate()
        assert_equal(self.app.post('/requires_token', expect_errors=True).status_code,
            401)

if __name__ == '__main__':
    unittest.main()
