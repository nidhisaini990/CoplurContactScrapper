import httpx
import pytest

from app.services.website_analyzer import _fetch_page, _is_public_host


@pytest.mark.asyncio
async def test_is_public_host_rejects_private_ip(monkeypatch):
    def fake_getaddrinfo(host, port):
        return [(None, None, None, None, ("127.0.0.1", 0))]

    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    assert await _is_public_host("internal.example") is False


@pytest.mark.asyncio
async def test_is_public_host_rejects_link_local_metadata_ip(monkeypatch):
    def fake_getaddrinfo(host, port):
        return [(None, None, None, None, ("169.254.169.254", 0))]

    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    assert await _is_public_host("metadata.example") is False


@pytest.mark.asyncio
async def test_is_public_host_accepts_public_ip(monkeypatch):
    def fake_getaddrinfo(host, port):
        return [(None, None, None, None, ("93.184.216.34", 0))]

    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    assert await _is_public_host("example.com") is True


@pytest.mark.asyncio
async def test_is_public_host_rejects_unresolvable_host(monkeypatch):
    import socket

    def fake_getaddrinfo(host, port):
        raise socket.gaierror("not found")

    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
    assert await _is_public_host("does-not-resolve.invalid") is False


@pytest.mark.asyncio
async def test_fetch_page_blocks_redirect_to_private_host(monkeypatch):
    def fake_getaddrinfo(host, port):
        if host == "public.example":
            return [(None, None, None, None, ("93.184.216.34", 0))]
        return [(None, None, None, None, ("127.0.0.1", 0))]

    monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://internal.example/secret"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await _fetch_page(client, "http://public.example/")

    assert result is None
