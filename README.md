# AI绘画插件 (ai_paint_siliconcloud)

[![License](https://img.shields.io/github/license/greenhandzdl/ai_paint_siliconcloud)](https://github.com/greenhandzdl/ai_paint_siliconcloud/blob/main/LICENSE)

这是为 [Nekro Agent](https://github.com/nekroai/nekro-agent) 开发的AI绘画插件，支持文生图和图生图功能，专为 SiliconCloud 平台定制。

## 功能特性

- **文生图**: 根据自然语言描述生成图片
- **图生图**: 基于参考图片生成新图片（风格迁移）
- **多模型支持**: 支持多种图像生成模型
- **可配置**: 可通过 Nekro Agent 配置系统进行详细配置

## 安装

1. 将此插件放置在 Nekro Agent 的插件目录中
2. 在 Nekro Agent 配置中启用插件

## 配置说明

在 Nekro Agent 的配置系统中，可以找到以下配置项：

### 绘图模型组
选择一个已配置好的、用于绘画的模型组。

### 绘图模型调用格式
- `图像生成`: 使用标准的 `/images/generations` API 接口
- `聊天模式`: 使用 `/chat/completions` 接口，通过多模态消息进行绘图
- `自动选择`: 插件会自动尝试并使用上次成功的模式

### 模型推理步数
控制图像生成的质量和时间，数值越高生成的图像质量越好但耗时越长。

### 绘图超时时间
由于绘图是耗时操作，可以设置一个较长的超时时间防止中断。

## 使用方法

### 与 AI 对话
直接对 AI 说 "画一只在晒太阳的橘猫"，AI 就会调用此插件来完成绘画。

示例提示词：
```
画一只在晒太阳的橘猫，水彩画风格
```

### 图生图（参考图片）
发送一张图片并告诉 AI 如何修改，例如"把背景换成樱花公园"，AI 会使用图生图功能来处理。

## 支持的模型

### Kolors
国产绘图模型，价格便宜，画风单一，效果一般，但速度较快
- 推荐配置:
  - `绘图模型调用格式`: 图像生成
  - `模型推理步数`: 20

## API 调用示例

插件内部会构造如下格式的 API 请求：

```bash
# https://docs.siliconflow.cn/cn/api-reference/images/images-generations
curl -X POST 'https://api.siliconflow.cn/v1/images/generations' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d '{
  "model": "Kwai-Kolors/Kolors",
  "prompt": "cat",
  "image_size": "1024x1024",
  "batch_size": 1,
  "seed": 123456789,
  "num_inference_steps": 20,
  "guidance_scale": 7.5
}'
```

## 故障排除

1. 如果图像生成失败，请检查 API 密钥是否正确配置
2. 如果生成的图像质量不佳，可以尝试增加 `模型推理步数`
3. 如果请求超时，请增加 `绘图超时时间` 配置

## 许可证

本项目采用 MIT 许可证，详情请见 [LICENSE](LICENSE) 文件。