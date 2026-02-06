"""Provider registry and factory for PaperBanana."""

from __future__ import annotations

import structlog

from paperbanana.core.config import Settings
from paperbanana.providers.base import ImageGenProvider, VLMProvider

logger = structlog.get_logger()


class ProviderRegistry:
    """Factory for creating VLM and image generation providers from config."""

    @staticmethod
    def create_vlm(settings: Settings) -> VLMProvider:
        """Create a VLM provider based on settings."""
        provider = settings.vlm_provider.lower()
        logger.info("Creating VLM provider", provider=provider, model=settings.vlm_model)

        if provider == "gemini":
            from paperbanana.providers.vlm.gemini import GeminiVLM

            api_key = settings.vlm_google_api_key or settings.google_api_key
            base_url = settings.vlm_google_genai_base_url or settings.google_genai_base_url
            auth_token = settings.vlm_google_genai_auth_token or settings.google_genai_auth_token
            auth_header = settings.vlm_google_genai_auth_header or settings.google_genai_auth_header
            use_vertexai = (
                settings.vlm_google_genai_use_vertexai
                if settings.vlm_google_genai_use_vertexai is not None
                else settings.google_genai_use_vertexai
            )

            return GeminiVLM(
                api_key=api_key,
                model=settings.vlm_model,
                base_url=base_url,
                auth_token=auth_token,
                auth_header=auth_header,
                use_vertexai=use_vertexai,
            )
        else:
            raise ValueError(f"Unknown VLM provider: {provider}. Available: gemini")

    @staticmethod
    def create_image_gen(settings: Settings) -> ImageGenProvider:
        """Create an image generation provider based on settings."""
        provider = settings.image_provider.lower()
        logger.info("Creating image gen provider", provider=provider, model=settings.image_model)

        if provider == "google_imagen":
            from paperbanana.providers.image_gen.google_imagen import GoogleImagenGen

            api_key = settings.image_google_api_key or settings.google_api_key
            base_url = settings.image_google_genai_base_url or settings.google_genai_base_url
            auth_token = settings.image_google_genai_auth_token or settings.google_genai_auth_token
            auth_header = (
                settings.image_google_genai_auth_header or settings.google_genai_auth_header
            )
            use_vertexai = (
                settings.image_google_genai_use_vertexai
                if settings.image_google_genai_use_vertexai is not None
                else settings.google_genai_use_vertexai
            )

            return GoogleImagenGen(
                api_key=api_key,
                model=settings.image_model,
                base_url=base_url,
                auth_token=auth_token,
                auth_header=auth_header,
                use_vertexai=use_vertexai,
            )
        else:
            raise ValueError(f"Unknown image provider: {provider}. Available: google_imagen")
