"""直接从已有的 planning.json 渲染图像，跳过 Retriever/Planner/Stylist。

用法:
    python render_from_planning.py <planning.json路径> [输出路径]

示例:
    python render_from_planning.py outputs/run_20260220_100903_c7483e/planning.json
    python render_from_planning.py outputs/run_20260220_100903_c7483e/planning.json outputs/v2.png
"""

import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from paperbanana.core.config import Settings
from paperbanana.core.types import DiagramType
from paperbanana.agents.visualizer import VisualizerAgent
from paperbanana.providers.registry import ProviderRegistry

# ── CLI 参数 ─────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="直接从已有的 planning.json 渲染图像，跳过 Retriever/Planner/Stylist")
parser.add_argument("planning_json", type=Path, help="planning.json 路径")
parser.add_argument("output_path", nargs="?", default="outputs/rerender.png", help="输出路径")
parser.add_argument("--config", default="configs/config.yaml", help="配置文件路径 (默认: configs/config.yaml)")
args = parser.parse_args()

planning_path: Path = args.planning_json
output_path: str = args.output_path

assert planning_path.exists(), f"找不到文件: {planning_path}"

planning = json.loads(planning_path.read_text())
description = planning["optimized_description"]

print(f"[*] 使用描述 ({len(description)} chars)")
print(f"[*] 输出到: {output_path}")

# ── 初始化 provider ───────────────────────────────────────────
config_path = Path(args.config)
settings = Settings.from_yaml(config_path) if config_path.exists() else Settings()
print(f"[*] 使用配置: {config_path} (resolution={settings.output_resolution})")
vlm = ProviderRegistry.create_vlm(settings)
image_gen = ProviderRegistry.create_image_gen(settings)

prompt_dir = Path(__file__).parent / "prompts"
assert prompt_dir.exists(), f"找不到 prompts 目录: {prompt_dir}"

Path(output_path).parent.mkdir(parents=True, exist_ok=True)

visualizer = VisualizerAgent(
    image_gen=image_gen,
    vlm_provider=vlm,
    prompt_dir=str(prompt_dir),
    output_dir=str(Path(output_path).parent),
    output_resolution=settings.output_resolution,
)


# ── 渲染 ─────────────────────────────────────────────────────
async def main():
    result_path = await visualizer.run(
        description=description,
        diagram_type=DiagramType.METHODOLOGY,
        output_path=output_path,
        iteration=1,
    )
    print(f"[done] 图像保存到: {result_path}")


asyncio.run(main())
