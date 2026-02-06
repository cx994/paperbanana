"""Tests for the provider registry."""

from __future__ import annotations

import pytest

from paperbanana.core.config import Settings
from paperbanana.providers.registry import ProviderRegistry


def test_create_gemini_vlm():
    """Test creating a Gemini VLM provider."""
    settings = Settings(
        vlm_provider="gemini",
        vlm_model="gemini-2.0-flash",
        google_api_key="test-key",
    )
    vlm = ProviderRegistry.create_vlm(settings)
    assert vlm.name == "gemini"
    assert vlm.model_name == "gemini-2.0-flash"


def test_create_google_imagen_gen():
    """Test creating a Google Imagen image gen provider."""
    settings = Settings(
        image_provider="google_imagen",
        google_api_key="test-key",
    )
    gen = ProviderRegistry.create_image_gen(settings)
    assert gen.name == "google_imagen"


def test_providers_available_with_custom_base_url():
    """Providers should be usable with a custom google-genai base_url (proxy/gateway)."""
    settings = Settings(
        vlm_provider="gemini",
        image_provider="google_imagen",
        google_genai_base_url="https://test-api-gateway-proxy.example.com",
        google_genai_auth_header="Bearer test_token",
    )

    vlm = ProviderRegistry.create_vlm(settings)
    gen = ProviderRegistry.create_image_gen(settings)
    assert vlm.is_available() is True
    assert gen.is_available() is True


def test_google_genai_auth_token_is_bearer_prefixed():
    """If only a token is provided, providers should build a Bearer Authorization header."""
    from paperbanana.providers.image_gen.google_imagen import GoogleImagenGen
    from paperbanana.providers.vlm.gemini import GeminiVLM

    vlm = GeminiVLM(auth_token="abc123")
    gen = GoogleImagenGen(auth_token="abc123")
    assert vlm._resolve_auth_header() == "Bearer abc123"
    assert gen._resolve_auth_header() == "Bearer abc123"


def test_component_specific_google_genai_settings_override_global():
    """VLM and Image providers should support separate base_url/keys via component overrides."""
    settings = Settings(
        vlm_provider="gemini",
        vlm_model="gemini-2.0-flash",
        image_provider="google_imagen",
        image_model="gemini-3-pro-image-preview",
        google_api_key="global-key",
        google_genai_base_url="https://global.example.com",
        google_genai_auth_header="Bearer global",
        google_genai_use_vertexai=True,
        vlm_google_api_key="vlm-key",
        vlm_google_genai_base_url="https://vlm.example.com",
        vlm_google_genai_auth_header="Bearer vlm",
        vlm_google_genai_use_vertexai=False,
        image_google_api_key="img-key",
        image_google_genai_base_url="https://img.example.com",
        image_google_genai_auth_header="Bearer img",
        image_google_genai_use_vertexai=True,
    )

    vlm = ProviderRegistry.create_vlm(settings)
    gen = ProviderRegistry.create_image_gen(settings)

    assert vlm._api_key == "vlm-key"
    assert vlm._base_url == "https://vlm.example.com"
    assert vlm._auth_header == "Bearer vlm"
    assert vlm._use_vertexai is False

    assert gen._api_key == "img-key"
    assert gen._base_url == "https://img.example.com"
    assert gen._auth_header == "Bearer img"
    assert gen._use_vertexai is True


def test_unknown_vlm_provider_raises():
    """Test that unknown VLM provider raises ValueError."""
    settings = Settings(vlm_provider="nonexistent")
    with pytest.raises(ValueError, match="Unknown VLM provider"):
        ProviderRegistry.create_vlm(settings)


def test_unknown_image_provider_raises():
    """Test that unknown image provider raises ValueError."""
    settings = Settings(image_provider="nonexistent")
    with pytest.raises(ValueError, match="Unknown image provider"):
        ProviderRegistry.create_image_gen(settings)
