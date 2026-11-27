# 🩺 ai-doctor

**One command. A full health check for your LLM API — with a score.**

[中文](README.md) · [Changelog](CHANGELOG.md)

```bash
AI_DOCTOR_KEY=sk-xxxx python3 ai_doctor.py --base https://api.openai.com/v1 --model gpt-4o-mini
```

Checks: model list reachability, chat latency (3 runs: min/median/max), streaming TTFT and throughput, JSON mode compliance, long-context intake, and a 0–100 score with an S–D grade. Zero dependencies (stdlib only); your API key is read from args/env and never stored. Works with any OpenAI-compatible endpoint: official APIs, relays, aggregators, and local gateways.

Sibling project: [server-doctor](https://github.com/yztutu/server-doctor) — the same idea for servers.

MIT licensed.
