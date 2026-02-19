"""Configuration management for PaperBanana."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class VLMConfig(BaseSettings):
    """VLM provider configuration."""

    provider: str = "gemini"
    model: str = "gemini-3-flash-preview"


class ImageConfig(BaseSettings):
    """Image generation provider configuration."""

    provider: str = "google_imagen"
    model: str = "gemini-3-pro-image-preview"


class PipelineConfig(BaseSettings):
    """Pipeline execution configuration."""

    num_retrieval_examples: int = 10
    refinement_iterations: int = 3
    output_resolution: str = "2k"
    diagram_type: str = "methodology"


class ReferenceConfig(BaseSettings):
    """Reference set configuration."""

    path: str = "data/reference_sets"
    guidelines_path: str = "data/guidelines"


class OutputConfig(BaseSettings):
    """Output configuration."""

    dir: str = "outputs"
    save_iterations: bool = True
    save_prompts: bool = True
    save_metadata: bool = True


class Settings(BaseSettings):
    """Main PaperBanana settings, loaded from env vars and config files."""

    # Provider settings
    vlm_provider: str = "gemini"
    vlm_model: str = "gemini-3-flash-preview"
    image_provider: str = "google_imagen"
    image_model: str = "gemini-3-pro-image-preview"

    # Pipeline settings
    num_retrieval_examples: int = 10
    refinement_iterations: int = 3
    output_resolution: str = "2k"

    # Reference settings
    reference_set_path: str = "data/reference_sets"
    guidelines_path: str = "data/guidelines"

    # Output settings
    output_dir: str = "outputs"
    save_iterations: bool = True

    # API Keys (loaded from environment)
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")

    # Google GenAI SDK (optional) — for API gateway/proxy setups
    # When GOOGLE_GENAI_BASE_URL is set, providers will construct a google-genai Client with:
    #   vertexai=True and http_options={"base_url": ..., "headers": {"Authorization": ...}}
    google_genai_base_url: Optional[str] = Field(default=None, alias="GOOGLE_GENAI_BASE_URL")
    google_genai_auth_token: Optional[str] = Field(default=None, alias="GOOGLE_GENAI_AUTH_TOKEN")
    google_genai_auth_header: Optional[str] = Field(
        default=None,
        alias="GOOGLE_GENAI_AUTHORIZATION",
    )
    google_genai_use_vertexai: Optional[bool] = Field(
        default=None, alias="GOOGLE_GENAI_USE_VERTEXAI"
    )

    # Per-component overrides (optional). If set, these take precedence over the global
    # GOOGLE_* values.
    # ── VLM ───────────────────────────────────────────────────────────
    vlm_google_api_key: Optional[str] = Field(default=None, alias="VLM_GOOGLE_API_KEY")
    vlm_google_genai_base_url: Optional[str] = Field(
        default=None, alias="VLM_GOOGLE_GENAI_BASE_URL"
    )
    vlm_google_genai_auth_token: Optional[str] = Field(
        default=None, alias="VLM_GOOGLE_GENAI_AUTH_TOKEN"
    )
    vlm_google_genai_auth_header: Optional[str] = Field(
        default=None,
        alias="VLM_GOOGLE_GENAI_AUTHORIZATION",
    )
    vlm_google_genai_use_vertexai: Optional[bool] = Field(
        default=None,
        alias="VLM_GOOGLE_GENAI_USE_VERTEXAI",
    )

    # ── Image Generation ──────────────────────────────────────────────
    image_google_api_key: Optional[str] = Field(default=None, alias="IMAGE_GOOGLE_API_KEY")
    image_google_genai_base_url: Optional[str] = Field(
        default=None, alias="IMAGE_GOOGLE_GENAI_BASE_URL"
    )
    image_google_genai_auth_token: Optional[str] = Field(
        default=None, alias="IMAGE_GOOGLE_GENAI_AUTH_TOKEN"
    )
    image_google_genai_auth_header: Optional[str] = Field(
        default=None,
        alias="IMAGE_GOOGLE_GENAI_AUTHORIZATION",
    )
    image_google_genai_use_vertexai: Optional[bool] = Field(
        default=None,
        alias="IMAGE_GOOGLE_GENAI_USE_VERTEXAI",
    )

    # SSL
    skip_ssl_verification: bool = Field(default=False, alias="SKIP_SSL_VERIFICATION")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }

    @classmethod
    def from_yaml(cls, config_path: str | Path, **overrides: Any) -> Settings:
        """Load settings from a YAML config file with optional overrides."""
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f) or {}
        else:
            yaml_config = {}

        flat = _flatten_yaml(yaml_config)
        flat.update(overrides)
        return cls(**flat)


def _flatten_yaml(config: dict, prefix: str = "") -> dict:
    """Flatten nested YAML config into flat settings keys."""
    flat = {}
    key_map = {
        "vlm.provider": "vlm_provider",
        "vlm.model": "vlm_model",
        "image.provider": "image_provider",
        "image.model": "image_model",
        "pipeline.num_retrieval_examples": "num_retrieval_examples",
        "pipeline.refinement_iterations": "refinement_iterations",
        "pipeline.output_resolution": "output_resolution",
        "reference.path": "reference_set_path",
        "reference.guidelines_path": "guidelines_path",
        "output.dir": "output_dir",
        "output.save_iterations": "save_iterations",
    }

    def _recurse(d: dict, prefix: str = "") -> None:
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                _recurse(v, full_key)
            else:
                if full_key in key_map:
                    flat[key_map[full_key]] = v

    _recurse(config)
    return flat
