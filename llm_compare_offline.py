"""
llm_compare_offline.py — Compare LLMs with NO API keys required
================================================================
Compares models on:
  - Benchmark scores (GPQA, HumanEval, MMLU-Pro, MATH-L5, SWE-bench, ARC)
  - Pricing (input/output cost per 1M tokens)
  - Context window size
  - Speed (typical tokens/sec from public reports)
  - Open vs closed source
  - Overall ranking

Usage:
    python llm_compare_offline.py
    python llm_compare_offline.py --models gpt-4o claude-sonnet gemini-2.5-pro
    python llm_compare_offline.py --sort cost
    python llm_compare_offline.py --category coding
    python llm_compare_offline.py --list

Install (optional, for pretty output):
    pip install rich
"""

import argparse
import statistics

# ─────────────────────────────────────────────────────────────
# MODEL DATABASE
# Edit this freely — add your own models or update scores.
#
# Fields:
#   provider, open_source, context_k (context window in K tokens),
#   price_in ($/1M input tokens), price_out ($/1M output tokens),
#   speed_tps (typical output tokens/sec, from public benchmarks),
#   benchmarks: [GPQA, HumanEval, MMLU-Pro, MATH-L5, SWE-bench, ARC]
# ─────────────────────────────────────────────────────────────

MODELS = {
    "gpt-4o": {
        "provider": "OpenAI", "open_source": False,
        "context_k": 128, "price_in": 2.50, "price_out": 10.00, "speed_tps": 68,
        "benchmarks": {"GPQA": 74, "HumanEval": 90, "MMLU-Pro": 82, "MATH-L5": 78, "SWE-bench": 60, "ARC": 94},
    },
    "gpt-4o-mini": {
        "provider": "OpenAI", "open_source": False,
        "context_k": 128, "price_in": 0.15, "price_out": 0.60, "speed_tps": 120,
        "benchmarks": {"GPQA": 53, "HumanEval": 82, "MMLU-Pro": 70, "MATH-L5": 65, "SWE-bench": 38, "ARC": 88},
    },
    "gpt-4.1": {
        "provider": "OpenAI", "open_source": False,
        "context_k": 1000, "price_in": 2.00, "price_out": 8.00, "speed_tps": 72,
        "benchmarks": {"GPQA": 78, "HumanEval": 92, "MMLU-Pro": 84, "MATH-L5": 80, "SWE-bench": 63, "ARC": 95},
    },
    "o3": {
        "provider": "OpenAI", "open_source": False,
        "context_k": 200, "price_in": 10.00, "price_out": 40.00, "speed_tps": 30,
        "benchmarks": {"GPQA": 87, "HumanEval": 95, "MMLU-Pro": 90, "MATH-L5": 91, "SWE-bench": 71, "ARC": 98},
    },
    "claude-opus-4.6": {
        "provider": "Anthropic", "open_source": False,
        "context_k": 200, "price_in": 15.00, "price_out": 75.00, "speed_tps": 42,
        "benchmarks": {"GPQA": 88, "HumanEval": 92, "MMLU-Pro": 85, "MATH-L5": 85, "SWE-bench": 72, "ARC": 96},
    },
    "claude-sonnet-4.6": {
        "provider": "Anthropic", "open_source": False,
        "context_k": 200, "price_in": 3.00, "price_out": 15.00, "speed_tps": 78,
        "benchmarks": {"GPQA": 80, "HumanEval": 88, "MMLU-Pro": 81, "MATH-L5": 80, "SWE-bench": 65, "ARC": 93},
    },
    "claude-haiku-4.5": {
        "provider": "Anthropic", "open_source": False,
        "context_k": 200, "price_in": 0.80, "price_out": 4.00, "speed_tps": 150,
        "benchmarks": {"GPQA": 62, "HumanEval": 78, "MMLU-Pro": 68, "MATH-L5": 63, "SWE-bench": 42, "ARC": 87},
    },
    "gemini-2.5-pro": {
        "provider": "Google", "open_source": False,
        "context_k": 1000, "price_in": 3.50, "price_out": 10.50, "speed_tps": 60,
        "benchmarks": {"GPQA": 86, "HumanEval": 91, "MMLU-Pro": 86, "MATH-L5": 87, "SWE-bench": 68, "ARC": 96},
    },
    "gemini-2.0-flash": {
        "provider": "Google", "open_source": False,
        "context_k": 1000, "price_in": 0.10, "price_out": 0.40, "speed_tps": 200,
        "benchmarks": {"GPQA": 70, "HumanEval": 83, "MMLU-Pro": 77, "MATH-L5": 72, "SWE-bench": 52, "ARC": 90},
    },
    "deepseek-r2": {
        "provider": "DeepSeek", "open_source": True,
        "context_k": 128, "price_in": 0.55, "price_out": 2.19, "speed_tps": 55,
        "benchmarks": {"GPQA": 84, "HumanEval": 90, "MMLU-Pro": 82, "MATH-L5": 88, "SWE-bench": 66, "ARC": 93},
    },
    "llama-4-scout": {
        "provider": "Meta", "open_source": True,
        "context_k": 128, "price_in": 0.18, "price_out": 0.59, "speed_tps": 90,
        "benchmarks": {"GPQA": 71, "HumanEval": 80, "MMLU-Pro": 74, "MATH-L5": 68, "SWE-bench": 48, "ARC": 89},
    },
    "llama-4-maverick": {
        "provider": "Meta", "open_source": True,
        "context_k": 128, "price_in": 0.27, "price_out": 0.85, "speed_tps": 75,
        "benchmarks": {"GPQA": 77, "HumanEval": 85, "MMLU-Pro": 79, "MATH-L5": 75, "SWE-bench": 55, "ARC": 91},
    },
    "grok-3": {
        "provider": "xAI", "open_source": False,
        "context_k": 131, "price_in": 3.00, "price_out": 15.00, "speed_tps": 65,
        "benchmarks": {"GPQA": 83, "HumanEval": 88, "MMLU-Pro": 80, "MATH-L5": 82, "SWE-bench": 60, "ARC": 92},
    },
    "mistral-large": {
        "provider": "Mistral", "open_source": False,
        "context_k": 128, "price_in": 2.00, "price_out": 6.00, "speed_tps": 80,
        "benchmarks": {"GPQA": 65, "HumanEval": 83, "MMLU-Pro": 73, "MATH-L5": 69, "SWE-bench": 44, "ARC": 89},
    },
    "qwen3-72b": {
        "provider": "Alibaba", "open_source": True,
        "context_k": 128, "price_in": 0.40, "price_out": 1.20, "speed_tps": 70,
        "benchmarks": {"GPQA": 75, "HumanEval": 86, "MMLU-Pro": 78, "MATH-L5": 80, "SWE-bench": 54, "ARC": 91},
    },
}

CATEGORY_BENCHMARKS = {
    "reasoning": ["GPQA", "ARC"],
    "coding":    ["HumanEval", "SWE-bench"],
    "math":      ["MATH-L5"],
    "knowledge": ["MMLU-Pro"],
    "all":       ["GPQA", "HumanEval", "MMLU-Pro", "MATH-L5", "SWE-bench", "ARC"],
}

SORT_OPTIONS = ["name", "cost", "speed", "context", "benchmark"]


# ─────────────────────────────────────────────────────────────
# COMPARISON LOGIC
# ─────────────────────────────────────────────────────────────

def get_avg_benchmark(model_data: dict, benches: list[str]) -> float:
    scores = [model_data["benchmarks"][b] for b in benches if b in model_data["benchmarks"]]
    return round(statistics.mean(scores), 1) if scores else 0.0

def cost_per_1k_tokens(model_data: dict) -> float:
    """Blended cost assuming 3:1 output:input ratio typical for chat."""
    return round((model_data["price_in"] * 0.25 + model_data["price_out"] * 0.75) / 1000, 6)

def rank_models(model_ids: list[str], sort_by: str, benches: list[str]) -> list[tuple]:
    rows = []
    for mid in model_ids:
        m = MODELS[mid]
        avg = get_avg_benchmark(m, benches)
        rows.append((mid, m, avg))

    if sort_by == "benchmark":
        rows.sort(key=lambda x: x[2], reverse=True)
    elif sort_by == "cost":
        rows.sort(key=lambda x: cost_per_1k_tokens(x[1]))
    elif sort_by == "speed":
        rows.sort(key=lambda x: x[1]["speed_tps"], reverse=True)
    elif sort_by == "context":
        rows.sort(key=lambda x: x[1]["context_k"], reverse=True)
    else:
        rows.sort(key=lambda x: x[0])

    return rows


# ─────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    from rich.text import Text
    RICH = True
except ImportError:
    RICH = False


def score_color(score: float) -> str:
    if score >= 85: return "green"
    if score >= 70: return "yellow"
    return "red"

def bar(value: float, max_val: float, width: int = 20) -> str:
    filled = int(round((value / max_val) * width))
    return "█" * filled + "░" * (width - filled)


def print_rich(rows, benches, sort_by, category):
    console = Console()
    console.print()
    console.print(f"[bold]LLM Comparison[/bold] — category: [cyan]{category}[/cyan]  sorted by: [cyan]{sort_by}[/cyan]")
    console.print()

    # ── Benchmark table ──────────────────────────
    t = Table(box=box.SIMPLE_HEAD, show_header=True, title="Benchmark scores (0–100)")
    t.add_column("#",  style="dim", width=3)
    t.add_column("Model", min_width=18)
    t.add_column("Provider", style="dim")
    t.add_column("OSS", justify="center", width=4)
    for b in benches:
        t.add_column(b, justify="right", width=10)
    t.add_column("Avg", justify="right", style="bold", width=6)

    for i, (mid, m, avg) in enumerate(rows, 1):
        scores = [str(m["benchmarks"].get(b, "—")) for b in benches]
        colored_scores = []
        for b, s in zip(benches, scores):
            val = m["benchmarks"].get(b, 0)
            colored_scores.append(Text(s, style=score_color(val)))
        oss = "Y" if m["open_source"] else "N"
        t.add_row(
            str(i), mid, m["provider"], oss,
            *colored_scores,
            Text(str(avg), style=score_color(avg))
        )
    console.print(t)

    # ── Cost & speed table ───────────────────────
    t2 = Table(box=box.SIMPLE_HEAD, title="Cost & speed")
    t2.add_column("Model", min_width=18)
    t2.add_column("In $/1M", justify="right")
    t2.add_column("Out $/1M", justify="right")
    t2.add_column("Blended $/1K", justify="right")
    t2.add_column("Context", justify="right")
    t2.add_column("Speed (tok/s)", justify="right")
    t2.add_column("Speed bar", width=22)

    max_speed = max(MODELS[mid]["speed_tps"] for mid, _, _ in rows)
    for mid, m, _ in rows:
        blend = cost_per_1k_tokens(m)
        spd = m["speed_tps"]
        t2.add_row(
            mid,
            f"${m['price_in']:.2f}",
            f"${m['price_out']:.2f}",
            f"${blend:.5f}",
            f"{m['context_k']}K",
            str(spd),
            f"[green]{bar(spd, max_speed)}[/green]",
        )
    console.print(t2)

    # ── Best picks ───────────────────────────────
    console.print()
    best_bench = max(rows, key=lambda x: x[2])
    best_cost  = min(rows, key=lambda x: cost_per_1k_tokens(x[1]))
    best_speed = max(rows, key=lambda x: x[1]["speed_tps"])
    console.print(f"[bold]Best benchmark avg:[/bold]  {best_bench[0]} ({best_bench[2]}%)")
    console.print(f"[bold]Cheapest:[/bold]            {best_cost[0]} (${cost_per_1k_tokens(best_cost[1]):.5f}/1K tok blended)")
    console.print(f"[bold]Fastest:[/bold]             {best_speed[0]} ({best_speed[1]['speed_tps']} tok/s)")
    console.print()


def print_plain(rows, benches, sort_by, category):
    sep = "-" * 80
    print(f"\nLLM Comparison | category: {category} | sorted by: {sort_by}")
    print(sep)

    header = f"{'#':<3} {'Model':<22} {'Provider':<12} {'OSS':<4}"
    for b in benches:
        header += f" {b:>10}"
    header += f" {'Avg':>6}"
    print(header)
    print(sep)

    for i, (mid, m, avg) in enumerate(rows, 1):
        row = f"{i:<3} {mid:<22} {m['provider']:<12} {'Y' if m['open_source'] else 'N':<4}"
        for b in benches:
            row += f" {str(m['benchmarks'].get(b, '—')):>10}"
        row += f" {avg:>6}"
        print(row)

    print(f"\n{'Model':<22} {'In$/1M':>8} {'Out$/1M':>9} {'Blend$/1K':>10} {'Context':>8} {'Tok/s':>6}")
    print(sep)
    for mid, m, _ in rows:
        blend = cost_per_1k_tokens(m)
        print(f"{mid:<22} {m['price_in']:>8.2f} {m['price_out']:>9.2f} {blend:>10.5f} {str(m['context_k'])+'K':>8} {m['speed_tps']:>6}")

    print()
    best_bench = max(rows, key=lambda x: x[2])
    best_cost  = min(rows, key=lambda x: cost_per_1k_tokens(x[1]))
    best_speed = max(rows, key=lambda x: x[1]["speed_tps"])
    print(f"Best benchmark avg : {best_bench[0]} ({best_bench[2]}%)")
    print(f"Cheapest           : {best_cost[0]} (${cost_per_1k_tokens(best_cost[1]):.5f}/1K blended)")
    print(f"Fastest            : {best_speed[0]} ({best_speed[1]['speed_tps']} tok/s)")


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compare LLMs — no API keys needed")
    parser.add_argument("--models", "-m", nargs="+", default=list(MODELS.keys()),
                        help="Model IDs to include (default: all)")
    parser.add_argument("--sort", "-s", default="benchmark", choices=SORT_OPTIONS,
                        help="Sort by: benchmark, cost, speed, context, name (default: benchmark)")
    parser.add_argument("--category", "-c", default="all",
                        choices=list(CATEGORY_BENCHMARKS.keys()),
                        help="Benchmark category to focus on (default: all)")
    parser.add_argument("--list", action="store_true",
                        help="List all available model IDs and exit")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable models:")
        for mid, m in MODELS.items():
            oss = "open-source" if m["open_source"] else "closed"
            print(f"  {mid:<24} {m['provider']:<12} {oss}")
        return

    unknown = [m for m in args.models if m not in MODELS]
    if unknown:
        print(f"Unknown model IDs: {unknown}")
        print(f"Run with --list to see available models.")
        return

    benches = CATEGORY_BENCHMARKS[args.category]
    rows = rank_models(args.models, args.sort, benches)

    if RICH:
        print_rich(rows, benches, args.sort, args.category)
    else:
        print_plain(rows, benches, args.sort, args.category)


if __name__ == "__main__":
    main()
