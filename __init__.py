
"""
# AI 绘画 (Draw)

赋予 AI 使用各种模型进行绘画创作的能力，支持文生图和图生图。

## 主要功能

- **文生图**: 根据用户或 AI 提供的自然语言描述（Prompt），生成一张全新的图片。
- **图生图 (图片参考)**: 在生成图片时，可以提供一张参考图，让 AI 模仿其风格或保留其元素。
- **多模型支持**: 可以接入任何兼容 OpenAI 格式的图像生成模型，并通过配置进行切换。

## 使用方法

- **与 AI 对话**: 直接对 AI 说 "画一只在晒太阳的橘猫"，AI 就会调用此插件来完成绘画。
- **修改图片**: 发送一张图片并告诉 AI 如何修改，例如"把背景换成樱花公园"，AI 会使用图生图功能来处理。

## 配置说明

- **绘图模型组**: 这是最重要的配置，您需要在这里选择一个已配置好的、用于绘画的模型组。
- **模型调用格式**:
  - `图像生成`: 使用标准的 `/images/generations` API 接口。
  - `聊天模式`: 使用 `/chat/completions` 接口，通过多模态消息进行绘图。
  - `自动选择`: 插件会自动尝试并使用上次成功的模式，推荐在不确定模型支持哪种格式时使用。
- **超时时间**: 由于绘图是耗时操作，可以设置一个较长的超时时间防止中断。

## 配置推荐预设参考

> 如果你的配置无法正常工作，请根据选择的模型参考以下配置进行调整

- **gemini-2.0-flash-exp-image-generation**: 使用 Gemini 模型进行绘图，支持文生图和图生图，效果较好
  - `是否使用系统角色`: 禁用 (**谷歌模型不支持系统角色**)
  - `绘图模型调用格式`: 聊天模式
  - `聊天模式使用流式 API`: 启用
- **sora_image**: 使用 Sora 模型进行绘图，支持文生图和图生图，效果非常好，支持精细化绘图指令，但速度较慢且价格较贵
  - `绘图模型调用格式`: 聊天模式
  - `绘图超时时间`: 300
- **Kolors**: 国产绘图模型，价格便宜，画风单一，效果一般，但速度较快
  - `绘图模型调用格式`: 图像生成
  - `模型推理步数`: 20
"""

import base64
import random
import re
from pathlib import Path
from typing import Literal, Optional

import aiofiles
import magic
from httpx import AsyncClient, Timeout
from pydantic import Field

from nekro_agent.api import core
from nekro_agent.api.plugin import ConfigBase, NekroPlugin, SandboxMethodType
from nekro_agent.api.schemas import AgentCtx
from nekro_agent.core import logger
from nekro_agent.core.config import config as global_config
from nekro_agent.services.agent.creator import ContentSegment, OpenAIChatMessage
from nekro_agent.services.agent.openai import gen_openai_chat_response
from nekro_agent.tools.common_util import limited_text_output
from nekro_agent.tools.path_convertor import convert_to_host_path

import json # For debug


# 创建插件实例
plugin = NekroPlugin(
    name="ai_paint_siliconcloud",
    module_name="ai_paint_siliconcloud",
    description="AI绘画（SiliconCloud定制版本)",
    version="0.1.3",
    author="greenhandzdl",
    url="https://github.com/greenhandzdl/ai_paint_siliconcloud",
)

@plugin.mount_config()
class DrawConfig(ConfigBase):
    """绘画配置"""

    USE_DRAW_MODEL_GROUP: str = Field(
        default="default-draw-chat",
        title="绘图模型组",
        json_schema_extra={"ref_model_groups": True, "required": True, "model_type": "draw"},
        description="主要使用的绘图模型组，可在 `系统配置` -> `模型组` 选项卡配置",
    )
    MODEL_MODE: Literal["自动选择（暂不可用）", "图像生成", "聊天模式（暂不可用）"] = Field(default="图像生成", title="绘图模型调用格式")
    NUM_INFERENCE_STEPS: int = Field(default=20, title="模型推理步数")
    USE_SYSTEM_ROLE: bool = Field(
        default=False,
        title="是否使用系统角色",
        description="只对聊天模式下的模型调用有效，如果启用时会把部分绘图提示词添加到系统角色中，如果模型不支持系统消息请关闭该选项",
    )
    STREAM_MODE: bool = Field(
        default=False,
        title="聊天模式使用流式 API",
        description="由于模型生成时间问题，部分模型需要在聊天模式下启用流式 API 才能正常工作",
    )
    TIMEOUT: int = Field(default=300, title="绘图超时时间", description="单位: 秒")


# 获取配置
config: DrawConfig = plugin.get_config(DrawConfig)


@plugin.mount_sandbox_method(SandboxMethodType.TOOL, name="绘图", description="支持文生图和图生图")
async def sdraw(
    _ctx: AgentCtx,
    prompt: str,
    size: str = "1024x1024",
    guidance_scale: float = 7.5,
    refer_image: str = "",
) -> str:
    """Generate or modify images

    Args:
        prompt (str): Natural language description of the image you want to create. (Only supports English)
            Suggested elements to include:
            - Type of drawing (e.g., character setting, landscape, comics, etc.)
            - What to draw details (characters, animals, objects, etc.)
            - What they are doing or their state
            - The scene or environment
            - Overall mood or atmosphere
            - Very detailed description or story (optional, recommend for comics)
            - Art style (e.g., illustration, watercolor... any style you want)

        size (str): Image dimensions (e.g., "1024x1024" square, "512x768" portrait, "768x512" landscape)
        guidance_scale (float): Guidance scale for the image generation, lower is more random, higher is more like the prompt (default: 7.5, from 0 to 20)
        refer_image (str): Optional source image path for image reference (useful for image style transfer or keep the elements of the original image)

    Returns:
        str: Generated image path

    Examples:
        # Generate new image but **NOT** send to chat
        draw("a illustration style cute orange cat napping on a sunny windowsill, watercolor painting style", "1024x1024")

        # Modify existing image
        send_msg_file(chat_key, draw("change the background to a cherry blossom park, keep the anime style", "1024x1024", "shared/refer_image.jpg")) # if adapter supports file, you can use this method to send the image to the chat. Otherwise, find another method to use the image.
    """

    # logger.info(f"绘图提示: {prompt}")
    # logger.info(f"绘图尺寸: {size}")
    # logger.info(f"使用绘图模型组: {config.USE_DRAW_MODEL_GROUP} 绘制: {prompt}")
    if refer_image:
        async with aiofiles.open(
            convert_to_host_path(Path(refer_image), chat_key=_ctx.chat_key, container_key=_ctx.container_key),
            mode="rb",
        ) as f:
            image_data = await f.read()
            mime_type = magic.from_buffer(image_data, mime=True)
            image_data = base64.b64encode(image_data).decode("utf-8")
        source_image_data = f"data:{mime_type};base64,{image_data}"
    else:
        source_image_data = "data:image/webp;base64, XXX"
    if config.USE_DRAW_MODEL_GROUP not in global_config.MODEL_GROUPS:
        raise Exception(f"绘图模型组 `{config.USE_DRAW_MODEL_GROUP}` 未配置")
    model_group = global_config.MODEL_GROUPS[config.USE_DRAW_MODEL_GROUP]

    return await _ctx.fs.mixed_forward_file(
        await _generate_image(model_group, prompt, size, config.NUM_INFERENCE_STEPS, guidance_scale, source_image_data),
    )

async def _generate_image(model_group, prompt, size, num_inference_steps, guidance_scale, source_image_data) -> str:
    """使用图像生成模式绘图"""
    # 构造请求链接
    url = f"{model_group.BASE_URL}/images/generations"
    
    # 构造请求头
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {model_group.API_KEY}",
    }
    
    # 构造请求体
    json_data = {
        "model": model_group.CHAT_MODEL,
        "prompt": prompt,
        "image_size": size,
        "batch_size": 1,
        "seed": random.randint(0, 9999999999),
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
    }

    # 合并打印信息为一条curl命令
    # curl_command = f"curl -X POST '{url}' \\\n"
    # curl_command += f"  -H 'Content-Type: application/json' \\\n"
    # curl_command += f"  -H 'Accept: application/json' \\\n"
    # curl_command += f"  -H 'Authorization: Bearer {model_group.API_KEY}' \\\n"
    # curl_command += f"  -d '{json.dumps(json_data, indent=2, ensure_ascii=False)}'"
    # logger.info(curl_command)

    async with AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            json=json_data,
            timeout=Timeout(read=config.TIMEOUT, write=config.TIMEOUT, connect=10, pool=10),
        )
    response.raise_for_status()
    data = response.json()
    ret_url = data["data"][0]["url"]
    if ret_url:
        return ret_url
    raise Exception(
        "No image content found in image generation AI response. You can adjust the prompt and try again. Make sure the prompt is clear and detailed.",
    )

@plugin.mount_cleanup_method()
async def clean_up():
    """清理插件"""