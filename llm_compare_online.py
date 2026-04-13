"""
llm_compare_online.py — Compare LLMs on responses, speed, cost, and benchmarks
========================================================================
Supports: OpenAI, Anthropic, Google Gemini, and any OpenAI-compatible endpoint.

Install dependencies:
    pip install openai anthropic google-generativeai rich

Usage:
    python llm_compare_online.py
    python llm_compare_online.py --prompt "Explain quantum entanglement in 2 sentences"
    python llm_compare_online.py --prompt "Write a haiku" --models gpt-4o claude-sonnet-4-6
"""

import os
import time
import argparse
import statistics
from dataclasses import dataclass, field
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich import box
    RICH = True
except ImportError:
    RICH = False

# ─────────────────────────────────────────────
# 1. MODEL REGISTRY
#    Add or remove models here freely.
# ─────────────────────────────────────────────

MODELS = {
    # id              provider       model string                  input $/1M   output $/1M
    "gpt-4o":        ("openai",     "gpt-4o",                     2.50,        10.00),
    "gpt-4o-mini":   ("openai",     "gpt-4o-mini",                0.15,         0.60),
    "gpt-4.1":       ("openai",     "gpt-4.1",                    2.00,         8.00),
    "o3":            ("openai",     "o3",                         10.00,        40.00),
    "claude-opus":   ("anthropic",  "claude-opus-4-6-20250514",   15.00,        75.00),
    "claude-sonnet": ("anthropic",  "claude-sonnet-4-6-20250514",  3.00,        15.00),
    "claude-haiku":  ("anthropic",  "claude-haiku-4-5-20251001",   0.80,         4.00),
    "gemini-2.5-pro":("google",     "gemini-2.5-pro",              3.50,        10.50),
    "gemini-2.0-flash":("google",   "gemini-2.0-flash",            0.10,         0.40),
}

# ─────────────────────────────────────────────
# 2. BENCHMARK SCORES (optional, edit freely)
#    Add your own model IDs and scores here.
#    Scale: 0-100. Leave out any you don't have.
# ─────────────────────────────────────────────

BENCHMARKS = {
    # model-id        GPQA   HumanEval  MMLU-Pro  MATH-L5  SWE-bench
    "gpt-4o":        [74,    90,        82,        78,       60],
    "gpt-4o-mini":   [53,    82,        70,        65,       38],
    "gpt-4.1":       [78,    92,        84,        80,       63],
    "o3":            [87,    95,        90,        91,       71],
    "claude-opus":   [88,    92,        85,        85,       72],
    "claude-sonnet": [80,    88,        81,        80,       65],
    "claude-haiku":  [62,    78,        68,        63,       42],
    "gemini-2.5-pro":[86,    91,        86,        87,       68],
    "gemini-2.0-flash":[70,  83,        77,        72,       52],
}
BENCHMARK_NAMES = ["GPQA", "HumanEval", "MMLU-Pro", "MATH-L5", "SWE-bench"]


# ─────────────────────────────────────────────
# 3. RESULT DATACLASS
# ─────────────────────────────────────────────

@dataclass
class Result:
    model_id: str
    provider: str
    response: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    tokens_per_sec: float = 0.0
    cost_usd: float = 0.0
    error: Optional[str] = None
    benchmarks: list = field(default_factory=list)


# ─────────────────────────────────────────────
# 4. PROVIDER CALLERS
# ─────────────────────────────────────────────

def call_openai(model_str: str, prompt: str) -> tuple:
    """Returns (response_text, input_tokens, output_tokens, latency_ms)"""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=model_str,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    latency_ms = (time.perf_counter() - t0) * 1000
    text = resp.choices[0].message.content or ""
    return text, resp.usage.prompt_tokens, resp.usage.completion_tokens, latency_ms


def call_anthropic(model_str: str, prompt: str) -> tuple:
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    t0 = time.perf_counter()
    resp = client.messages.create(
        model=model_str,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    latency_ms = (time.perf_counter() - t0) * 1000
    text = resp.content[0].text if resp.content else ""
    return text, resp.usage.input_tokens, resp.usage.output_tokens, latency_ms


def call_google(model_str: str, prompt: str) -> tuple:
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError("google-generativeai not installed. Run: pip install google-generativeai")

    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_str)
    t0 = time.perf_counter()
    resp = model.generate_content(prompt)
    latency_ms = (time.perf_counter() - t0) * 1000
    text = resp.text or ""
    # Google doesn't always return token counts, estimate from chars
    input_tok = len(prompt) // 4
    output_tok = len(text) // 4
    return text, input_tok, output_tok, latency_ms


CALLERS = {
    "openai":    call_openai,
    "anthropic": call_anthropic,
    "google":    call_google,
}


# ─────────────────────────────────────────────
# 5. CORE COMPARISON FUNCTION
# ─────────────────────────────────────────────

def compare(prompt: str, model_ids: list[str]) -> list[Result]:
    results = []

    for mid in model_ids:
        if mid not in MODELS:
            print(f"[skip] Unknown model: {mid}")
            continue

        provider, model_str, price_in, price_out = MODELS[mid]
        print(f"  Calling {mid} ({provider})...", end=" ", flush=True)

        r = Result(model_id=mid, provider=provider)

        try:
            caller = CALLERS[provider]
            text, in_tok, out_tok, latency = caller(model_str, prompt)

            r.response = text
            r.input_tokens = in_tok
            r.output_tokens = out_tok
            r.latency_ms = round(latency, 1)
            r.tokens_per_sec = round((out_tok / latency) * 1000, 1) if latency > 0 else 0
            r.cost_usd = round((in_tok * price_in + out_tok * price_out) / 1_000_000, 6)
            r.benchmarks = BENCHMARKS.get(mid, [])
            print(f"done ({latency:.0f}ms)")

        except Exception as e:
            r.error = str(e)
            print(f"ERROR: {e}")

        results.append(r)

    return results


# ─────────────────────────────────────────────
# 6. OUTPUT / DISPLAY
# ─────────────────────────────────────────────

def print_results(results: list[Result], prompt: str):
    if RICH:
        _print_rich(results, prompt)
    else:
        _print_plain(results, prompt)


def _print_rich(results: list[Result], prompt: str):
    console = Console()
    console.print()
    console.print(Panel(f"[bold]Prompt:[/bold] {prompt}", expand=False))

    # ── Responses ──────────────────────────────
    console.print("\n[bold]Responses[/bold]")
    panels = []
    for r in results:
        if r.error:
            content = f"[red]Error: {r.error}[/red]"
        else:
            content = r.response[:600] + ("…" if len(r.response) > 600 else "")
        panels.append(Panel(content, title=r.model_id, expand=True))
    console.print(Columns(panels))

    # ── Speed & Cost ───────────────────────────
    console.print("\n[bold]Speed & Cost[/bold]")
    t = Table(box=box.SIMPLE_HEAD, show_header=True)
    for col in ["Model", "Provider", "Latency (ms)", "Tokens/sec", "In tokens", "Out tokens", "Cost (USD)"]:
        t.add_column(col, style="dim" if col == "Provider" else "")
    for r in results:
        if r.error:
            t.add_row(r.model_id, r.provider, "—", "—", "—", "—", f"[red]{r.error[:30]}[/red]")
        else:
            t.add_row(
                r.model_id, r.provider,
                str(r.latency_ms),
                str(r.tokens_per_sec),
                str(r.input_tokens),
                str(r.output_tokens),
                f"${r.cost_usd:.6f}",
            )
    console.print(t)

    # ── Benchmarks ─────────────────────────────
    bench_results = [r for r in results if r.benchmarks]
    if bench_results:
        console.print("\n[bold]Benchmark scores[/bold]")
        bt = Table(box=box.SIMPLE_HEAD)
        bt.add_column("Model")
        for name in BENCHMARK_NAMES:
            bt.add_column(name, justify="right")
        bt.add_column("Avg", justify="right", style="bold")
        for r in bench_results:
            scores = r.benchmarks
            avg = round(statistics.mean(scores), 1)
            bt.add_row(r.model_id, *[str(s) for s in scores], str(avg))
        console.print(bt)


def _print_plain(results: list[Result], prompt: str):
    sep = "-" * 60
    print(f"\nPrompt: {prompt}\n{sep}")
    for r in results:
        print(f"\n=== {r.model_id} ({r.provider}) ===")
        if r.error:
            print(f"ERROR: {r.error}")
        else:
            print(f"Response:\n{r.response[:500]}")
            print(f"\nLatency: {r.latency_ms}ms | Tokens/sec: {r.tokens_per_sec}")
            print(f"Tokens: {r.input_tokens} in / {r.output_tokens} out | Cost: ${r.cost_usd:.6f}")
            if r.benchmarks:
                bench_str = " | ".join(f"{n}: {s}" for n, s in zip(BENCHMARK_NAMES, r.benchmarks))
                avg = round(statistics.mean(r.benchmarks), 1)
                print(f"Benchmarks: {bench_str} | Avg: {avg}")
    print(f"\n{sep}")


# ─────────────────────────────────────────────
# 7. CLI ENTRY POINT
# ─────────────────────────────────────────────

DEFAULT_PROMPT = "Explain the difference between supervised and unsupervised learning in 3 sentences."

DEFAULT_MODELS = ["gpt-4o", "claude-sonnet", "gemini-2.5-pro"]

def main():
    parser = argparse.ArgumentParser(description="Compare LLM models side by side")
    parser.add_argument("--prompt", "-p", default=DEFAULT_PROMPT, help="Prompt to send to all models")
    parser.add_argument("--models", "-m", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()), help="Model IDs to compare")
    parser.add_argument("--list", action="store_true", help="List all available model IDs and exit")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable models:")
        for mid, (prov, mstr, pi, po) in MODELS.items():
            print(f"  {mid:<22} {prov:<12} in=${pi}/1M  out=${po}/1M")
        return

    print(f"\nComparing {len(args.models)} models...")
    results = compare(args.prompt, args.models)
    print_results(results, args.prompt)


if __name__ == "__main__":
    main()
