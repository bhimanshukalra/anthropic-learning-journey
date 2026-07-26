import argparse
from typing import Any

from claude_helpers import CLAUDE_MODEL, client, extract_text

MAX_TOKENS = 300

SHARED_REFERENCE = """
You are an API architecture reviewer. Use the following internal guidance when
answering questions about AI application design.

Core principles:
- Keep provider API keys on the server.
- Validate model outputs before using them in business logic.
- Prefer structured outputs for machine-readable responses.
- Stream long responses when the user benefits from early feedback.
- Use prompt caching for stable, repeated prompt prefixes.
- Use tool calls only when the model needs information or actions from systems
  outside its context.
- Keep tool permissions narrow and auditable.
- Measure cost, latency, and quality for every user-facing AI feature.
- Treat prompts, schemas, and eval datasets as versioned production assets.
- Prefer small, explicit loops over hidden framework behavior while learning.

Operational checklist:
1. Define the user-facing job to be done.
2. Decide whether the feature needs retrieval, tools, structured output, or only
   a direct model call.
3. Write the smallest prompt that expresses role, constraints, and output shape.
4. Add validation around the model response.
5. Add retries only around known recoverable failures.
6. Log model, token usage, latency, cache reads, cache writes, and final status.
7. Add tests for normal inputs, edge cases, and adversarial prompts.
8. Convert real failures into eval cases.
9. Keep cost budgets visible.
10. Keep rollback simple.
""" * 12


def cached_system_prompt(ttl: str = "5m") -> list[dict[str, Any]]:
    # cache_control belongs on the stable block you expect to reuse across calls.
    # Here, the long system prompt is stable while each user question changes.
    cache_control = {"type": "ephemeral"}
    if ttl == "1h":
        # 5 minutes is the default. Use 1h only when the prefix is worth keeping
        # warm longer, because writes are more expensive than normal input tokens.
        cache_control["ttl"] = "1h"

    return [
        {
            "type": "text",
            "text": SHARED_REFERENCE,
            "cache_control": cache_control,
        }
    ]


def print_cache_usage(label: str, message: Any) -> None:
    # A first request usually writes cache tokens; a matching later request
    # should show cache_read_input_tokens when the prefix is reused.
    usage = message.usage
    cache_creation = getattr(usage, "cache_creation", None)

    print(label)
    print(f"- Input tokens: {usage.input_tokens}")
    print(f"- Output tokens: {usage.output_tokens}")
    print(f"- Cache creation input tokens: {getattr(usage, 'cache_creation_input_tokens', 0)}")
    print(f"- Cache read input tokens: {getattr(usage, 'cache_read_input_tokens', 0)}")
    if cache_creation:
        print(f"- Cache creation detail: {cache_creation}")
    print()


def ask_with_automatic_cache(question: str) -> Any:
    # Automatic caching lets the API choose the last cacheable block as the
    # breakpoint and move it forward as the conversation grows.
    return client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        cache_control={"type": "ephemeral"},
        system=SHARED_REFERENCE,
        messages=[{"role": "user", "content": question}],
    )


def ask_with_explicit_system_cache(question: str, *, ttl: str = "5m") -> Any:
    # Explicit caching is useful when you know exactly which stable prefix should
    # be reused, such as a long system prompt or policy document.
    return client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=cached_system_prompt(ttl),
        messages=[{"role": "user", "content": question}],
    )


def prewarm_system_cache(*, ttl: str = "5m") -> Any:
    # max_tokens=0 writes the cache without asking Claude to produce an answer.
    # The follow-up request must reuse the same cached prefix to get a cache hit.
    return client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=0,
        system=cached_system_prompt(ttl),
        messages=[{"role": "user", "content": "warmup"}],
    )


def run_twice(label: str, first_question: str, second_question: str, request_fn) -> None:
    # The two questions differ on purpose. Cache hits depend on the shared prefix,
    # not on the user question being identical.
    first = request_fn(first_question)
    print_cache_usage(f"{label}: first request", first)
    print("First response:")
    print(extract_text(first))
    print()

    second = request_fn(second_question)
    print_cache_usage(f"{label}: second request", second)
    print("Second response:")
    print(extract_text(second))


def run_automatic_demo() -> None:
    run_twice(
        "Automatic caching",
        "Summarize the operational checklist in 3 bullets.",
        "Which checklist items are most relevant for tool-using agents?",
        ask_with_automatic_cache,
    )


def run_explicit_demo(ttl: str) -> None:
    run_twice(
        f"Explicit system-prompt caching ({ttl})",
        "What should I log for a production AI feature?",
        "How would prompt caching change cost and latency for repeated requests?",
        lambda question: ask_with_explicit_system_cache(question, ttl=ttl),
    )


def run_prewarm_demo(ttl: str) -> None:
    # Prewarming separates cache creation from the user-facing request.
    warmup = prewarm_system_cache(ttl=ttl)
    print_cache_usage(f"Prewarm request ({ttl})", warmup)

    response = ask_with_explicit_system_cache(
        "After prewarming, explain the purpose of prompt caching in 2 sentences.",
        ttl=ttl,
    )
    print_cache_usage("Request after prewarm", response)
    print("Response:")
    print(extract_text(response))


def build_parser() -> argparse.ArgumentParser:
    # Keep the modes separate so cache behavior is easy to compare in terminal output.
    parser = argparse.ArgumentParser(description="Claude prompt caching examples.")
    parser.add_argument(
        "mode",
        choices=["automatic", "explicit", "prewarm"],
        help="Prompt caching pattern to run.",
    )
    parser.add_argument(
        "--ttl",
        choices=["5m", "1h"],
        default="5m",
        help="TTL for explicit cache_control breakpoints.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.mode == "automatic":
        run_automatic_demo()
    elif args.mode == "explicit":
        run_explicit_demo(args.ttl)
    elif args.mode == "prewarm":
        run_prewarm_demo(args.ttl)


if __name__ == "__main__":
    main()
