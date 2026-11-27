# 🩺 ai-doctor

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-yellow)](#)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)](#)

[English](README_EN.md) · [更新日志](CHANGELOG.md) · [常见问题](docs/faq.md)

**一条命令，给你的 AI 接口做一次全身体检，最后打个分。**

买的中转、聚合站、自建网关到底稳不稳、快不快、是不是真模型？跑一遍就知道。

```bash
AI_DOCTOR_KEY=sk-xxxx python3 ai_doctor.py --base https://api.openai.com/v1 --model gpt-4o-mini
```

## 测什么

| 项目 | 内容 |
| --- | --- |
| 连通性 | 模型列表端点可达性与延迟、模型总数 |
| 对话质量 | 连测 3 次：最快/中位/最慢延迟、token 用量回执 |
| 流式速度 | 首字时间（TTFT）、每秒输出块数——打字机快慢一眼见分晓 |
| JSON 模式 | 是否真支持结构化输出，还是假装支持 |
| 长上下文 | 一次喂 ~4 万字符，看它吃不吃得下、回执多少 token |
| 评分 | 百分制扣分，S–D 评级；`--json` 输出机器可读报告 |

## 设计原则

- **零依赖**：只用 Python 标准库，任何机器 `python3` 就能跑
- **不存密钥**：key 只从参数/环境变量读，用完即走，绝不落盘
- **兼容一切 OpenAI 格式接口**：官方、Azure、中转站、聚合站、本地 Ollama/LM Studio 网关

## 姊妹项目

[server-doctor](https://github.com/yztutu/server-doctor) — 给服务器做体检的那个。

## License

MIT
