#!/usr/bin/env python3
"""ai-doctor — one-command health check for OpenAI-compatible LLM APIs.
Zero dependencies (stdlib only). Your key is read from args/env, never stored.
Usage:
  AI_DOCTOR_KEY=sk-... python3 ai_doctor.py --base https://api.openai.com/v1 --model gpt-4o-mini
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

VERSION = "1.0.0"

def req(method, url, key, body=None, stream=False, timeout=30):
    r = urllib.request.Request(url, method=method)
    r.add_header("Authorization", f"Bearer {key}")
    r.add_header("Content-Type", "application/json")
    data = json.dumps(body).encode() if body is not None else None
    return urllib.request.urlopen(r, data=data, timeout=timeout)

def timed(fn):
    t0 = time.time()
    try:
        out = fn()
        return out, (time.time() - t0) * 1000, None
    except urllib.error.HTTPError as e:
        return None, (time.time() - t0) * 1000, f"HTTP {e.code}: {e.read()[:200].decode('utf-8','ignore')}"
    except Exception as e:
        return None, (time.time() - t0) * 1000, f"{type(e).__name__}: {e}"

def main():
    ap = argparse.ArgumentParser(description="AI API health check")
    ap.add_argument("--base", default=os.environ.get("AI_DOCTOR_BASE", "https://api.openai.com/v1"))
    ap.add_argument("--key", default=os.environ.get("AI_DOCTOR_KEY", ""))
    ap.add_argument("--model", default=os.environ.get("AI_DOCTOR_MODEL", ""))
    ap.add_argument("--json", action="store_true", help="also write /tmp/ai-doctor.json")
    ap.add_argument("--version", action="store_true")
    a = ap.parse_args()
    if a.version:
        print(f"ai-doctor {VERSION}"); return
    base = a.base.rstrip("/")
    if not a.key:
        print("✗ 缺少 API key：用 --key 或环境变量 AI_DOCTOR_KEY 传入（不会保存）"); sys.exit(2)
    score = 100; notes = []
    def deduct(n, msg):
        nonlocal score; score = max(0, score - n); notes.append(msg)
    print(f"🩺 ai-doctor v{VERSION}  接口体检：{base}")
    print("─" * 46)

    # 1) models list
    resp, ms, err = timed(lambda: req("GET", f"{base}/models", a.key, timeout=15))
    models = []
    if resp is not None:
        d = json.loads(resp.read())
        models = [m.get("id", "") for m in d.get("data", [])]
        print(f"✓ 模型列表可达（{ms:.0f} ms），共 {len(models)} 个模型")
    else:
        print(f"✗ 模型列表失败：{err}"); deduct(30, "models 端点异常")
    model = a.model or (models[0] if models else "")
    if a.model and models and a.model not in models:
        print(f"! 指定模型 {a.model} 不在列表里（可能仍可用）")
    if not model:
        print("✗ 没有可用模型名，终止"); sys.exit(1)
    print(f"  测试模型：{model}")

    # 2) basic chat completion, 3 runs for latency spread
    body = {"model": model, "messages": [{"role": "user", "content": "Reply with exactly: pong"}], "max_tokens": 8, "temperature": 0}
    lat = []; usage = {}
    for i in range(3):
        resp, ms, err = timed(lambda: req("POST", f"{base}/chat/completions", a.key, body, timeout=60))
        if resp is not None:
            d = json.loads(resp.read()); lat.append(ms); usage = d.get("usage", {}) or usage
            if i == 0:
                txt = (d.get("choices", [{}])[0].get("message", {}) or {}).get("content", "")
                print(f"✓ 对话可用，返回：{txt.strip()[:40]!r}")
        else:
            print(f"✗ 对话失败：{err}"); deduct(40, "chat 端点异常"); break
    if lat:
        lat_s = sorted(lat)
        print(f"  延迟  最快 {lat_s[0]:.0f} ms · 中位 {lat_s[len(lat_s)//2]:.0f} ms · 最慢 {lat_s[-1]:.0f} ms")
        if lat_s[len(lat_s)//2] > 5000: deduct(10, "延迟偏高")
        if usage:
            print(f"  用量示例：prompt {usage.get('prompt_tokens')} · completion {usage.get('completion_tokens')} tokens")

    # 3) streaming: TTFT + tokens/sec
    sbody = {"model": model, "messages": [{"role": "user", "content": "Count from 1 to 40, comma separated."}],
             "max_tokens": 200, "temperature": 0, "stream": True}
    def stream_test():
        r = req("POST", f"{base}/chat/completions", a.key, sbody, stream=True, timeout=60)
        t0 = time.time(); ttft = None; chunks = 0
        for raw in r:
            line = raw.decode("utf-8", "ignore").strip()
            if line.startswith("data:") and line[5:].strip() != "[DONE]":
                if ttft is None: ttft = (time.time() - t0) * 1000
                chunks += 1
        return ttft, chunks, (time.time() - t0) * 1000
    out, _, err = timed(stream_test)
    if out and out[0] is not None:
        ttft, chunks, total = out
        tps = chunks / (total / 1000) if total > 0 else 0
        print(f"✓ 流式可用：首字 {ttft:.0f} ms · 约 {tps:.1f} chunks/s · 总 {total:.0f} ms")
        if ttft > 3000: deduct(10, "首字慢")
    else:
        print(f"! 流式不可用或无数据：{err or out}"); deduct(10, "流式异常")

    # 4) JSON mode
    jbody = {"model": model, "messages": [{"role": "user", "content": "Return a JSON object with key ok=true only."}],
             "max_tokens": 30, "temperature": 0, "response_format": {"type": "json_object"}}
    resp, ms, err = timed(lambda: req("POST", f"{base}/chat/completions", a.key, jbody, timeout=60))
    if resp is not None:
        d = json.loads(resp.read())
        txt = (d.get("choices", [{}])[0].get("message", {}) or {}).get("content", "")
        try:
            json.loads(txt); print("✓ JSON 模式可用")
        except Exception:
            print("! JSON 模式返回了非 JSON 内容"); deduct(5, "JSON 模式不规范")
    else:
        print(f"! JSON 模式不支持/失败：{err}"); deduct(5, "JSON 模式失败")

    # 5) long-context probe (32k chars)
    big = "The quick brown fox jumps over the lazy dog. " * 900
    lbody = {"model": model, "messages": [{"role": "user", "content": big + "\nHow many sentences did I send? Just give the number."}],
             "max_tokens": 10, "temperature": 0}
    resp, ms, err = timed(lambda: req("POST", f"{base}/chat/completions", a.key, lbody, timeout=90))
    if resp is not None:
        d = json.loads(resp.read()); u = d.get("usage", {})
        print(f"✓ 长上下文可用：一次吃下 {u.get('prompt_tokens', '?')} tokens（{ms:.0f} ms）")
    else:
        print(f"! 长上下文失败（可能上限较小）：{err}"); deduct(5, "长上下文失败")

    grade = "S · 极品" if score >= 90 else "A · 优秀" if score >= 80 else "B · 良好" if score >= 65 else "C · 一般" if score >= 50 else "D · 较差"
    print("─" * 46)
    print(f"体检评分：{score} / 100 — {grade}")
    if a.json:
        json.dump({"tool": "ai-doctor", "version": VERSION, "base": base, "model": model,
                   "score": score, "grade": grade, "models_count": len(models), "notes": notes},
                  open("/tmp/ai-doctor.json", "w"), ensure_ascii=False, indent=2)
        print("JSON 已存到 /tmp/ai-doctor.json")

if __name__ == "__main__":
    main()
