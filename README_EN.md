# 🔍 ai-doctor — the LLM API inspector

**Before you pay for an AI API, inspect the goods.**

Relays and aggregators are everywhere: flagship prices for downgraded models, silent rate limits, fake JSON mode. ai-doctor runs your key through a full inspection and tells you what you actually bought.

```
$ AI_DOCTOR_KEY=sk-xxxx python3 ai_doctor.py --base https://api.example.com/v1 --model gpt-4o-mini
✓ models reachable (212 ms), 31 models
✓ chat works — latency min 480 / median 620 / max 910 ms
✓ streaming: TTFT 390 ms · ~42 chunks/s
✓ JSON mode: genuinely supported
✓ long context: swallowed 10,350 tokens in one go
Score: 100 / 100 — S tier
```

**The checklist:** model list vs. what's advertised · latency over 3 runs · streaming TTFT & throughput · real JSON-mode compliance · long-context intake · a final 0–100 score (S–D).

Zero dependencies (Python stdlib only). Your key never leaves your machine and is never stored. Works with any OpenAI-compatible endpoint — official, relay, aggregator, or local gateway.

Sibling tool: [server-doctor](https://github.com/yztutu/server-doctor) — the same idea, for servers.

MIT licensed.
