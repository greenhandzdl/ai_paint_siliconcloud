# AI绘画插件 (ai_paint_siliconcloud)

[![License](https://img.shields.io/github/license/greenhandzdl/ai_paint_siliconcloud)](https://github.com/greenhandzdl/ai_paint_siliconcloud/blob/main/LICENSE)

> ⚠️ **重要警告**: 此插件中AI修改负面提示词的行为不可控，可能导致生成不符合预期的图像。**强烈不推荐使用本插件**。

推荐用户使用Nekro Agent内置的draw插件，该插件添加对负面提示词的支持（PR [#118](https://github.com/KroMiose/nekro-agent/pull/118)），是更安全可靠的替代方案。

这是为 [Nekro Agent](https://github.com/nekroai/nekro-agent) 开发的AI绘画插件，支持文生图和图生图功能，专为 SiliconCloud 平台定制。

## 功能特性

- **文生图**: 根据自然语言描述生成图片
- **图生图**: 基于参考图片生成新图片（风格迁移）
- **多模型支持**: 支持多种图像生成模型
- **可配置**: 可通过 Nekro Agent 配置系统进行详细配置

## ⚠️ 重要警告

此插件中AI修改负面提示词的行为**不可控**，可能导致：
- 生成图像包含不希望出现的内容
- 图像质量不稳定
- 无法准确预测和控制AI对负面提示词的修改行为

**强烈不推荐用户使用本插件**，推荐使用Nekro Agent内置的draw插件。

## 安装

1. 将此插件放置在 Nekro Agent 的插件目录中
2. 在 Nekro Agent 配置中启用插件

## 配置说明

### 主要配置项
- **绘图模型组**: 选择已配置好的绘画模型组
- **绘图模型调用格式**: 图像生成 / 聊天模式 / 自动选择
- **模型推理步数**: 控制图像生成质量和时间
- **绘图超时时间**: 设置较长的超时时间防止中断

## 使用方法

直接对 AI 说 "画一只在晒太阳的橘猫"，AI 就会调用此插件来完成绘画。

示例提示词：
```
画一只在晒太阳的橘猫，水彩画风格
```

## 支持的模型

### Kolors
国产绘图模型，价格便宜，画风单一，效果一般，但速度较快
- 推荐配置:
  - `绘图模型调用格式`: 图像生成
  - `模型推理步数`: 20

## 许可证

本项目采用 MIT 许可证，详情请见 [LICENSE](LICENSE) 文件。