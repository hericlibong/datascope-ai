# backend/ai_engine/tests/test_url_validator.py

import requests
import responses

from ai_engine.services import validate_url


@responses.activate
def test_validate_ok_200_head():
    url = "https://example.org/data"
    responses.add(responses.HEAD, url, status=200)

    res = validate_url(url)
    assert res["status"] == "ok"
    assert res["http_status"] == 200
    assert res["final_url"] == url
    assert res["error"] is None


@responses.activate
def test_validate_redirect_301_to_200():
    src = "https://example.org/old"
    dst = "https://example.org/new"
    responses.add(responses.HEAD, src, status=301, headers={"Location": dst})
    responses.add(responses.HEAD, dst, status=200)

    res = validate_url(src)
    assert res["status"] in ("redirected", "ok")  # redirected attendu
    assert res["http_status"] == 200
    assert res["final_url"] == dst


@responses.activate
def test_validate_head_405_fallback_get_200():
    url = "https://example.org/head-not-allowed"
    responses.add(responses.HEAD, url, status=405)
    responses.add(responses.GET, url, status=200)

    res = validate_url(url)
    assert res["status"] == "ok"
    assert res["http_status"] == 200
    assert res["final_url"] == url


@responses.activate
def test_validate_not_found_404():
    url = "https://example.org/missing"
    responses.add(responses.HEAD, url, status=404)

    res = validate_url(url)
    assert res["status"] == "not_found"
    assert res["http_status"] == 404
    assert res["final_url"] == url


@responses.activate
def test_validate_server_error_500():
    url = "https://example.org/boom"
    responses.add(responses.HEAD, url, status=500)

    res = validate_url(url)
    assert res["status"] == "error"
    assert res["http_status"] == 500
    assert res["error"] == "HTTP 500"


@responses.activate
def test_validate_timeout():
    url = "https://example.org/slow"
    responses.add(responses.HEAD, url, body=requests.exceptions.Timeout())

    res = validate_url(url)
    assert res["status"] == "error"
    assert res["http_status"] is None
    assert res["error"] == "Timeout"
