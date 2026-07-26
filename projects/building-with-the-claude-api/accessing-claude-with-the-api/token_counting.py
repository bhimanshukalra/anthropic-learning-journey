import argparse
from dataclasses import dataclass
from typing import Any

from claude_helpers import CLAUDE_MODEL, client
from multimodal_input import image_block_from_url
from tool_use import TOOLS

MODEL_CONTEXT_LIMITS = {
    "claude-sonnet-4-5": 200_000,
}


@dataclass(frozen=True)
class ModelPricing:
    input_per_million: float
    output_per_million: float


MODEL_PRICING = {
    # Update these constants when your target model pricing changes.
    "claude-sonnet-4-5": ModelPricing(input_per_million=3.0, output_per_million=15.0),
}


def count_tokens(
    messages: list[dict[str, Any]],
    *,
    system: str | list[dict[str, Any]] | None = None,
    tools: list[dict[str, Any]] | None = None,
) -> int:
    params = {
        "model": CLAUDE_MODEL,
        "messages": messages,
    }
    if system:
        params["system"] = system
    if tools:
        params["tools"] = tools

    token_count = client.messages.count_tokens(**params)
    return token_count.input_tokens


def estimate_cost(input_tokens: int, output_tokens: int, *, model: str = CLAUDE_MODEL) -> float:
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        raise ValueError(f"No pricing configured for model: {model}")

    input_cost = (input_tokens / 1_000_000) * pricing.input_per_million
    output_cost = (output_tokens / 1_000_000) * pricing.output_per_million
    return input_cost + output_cost


def print_estimate(label: str, input_tokens: int, expected_output_tokens: int = 500) -> None:
    context_limit = MODEL_CONTEXT_LIMITS.get(CLAUDE_MODEL)
    estimated_cost = estimate_cost(input_tokens, expected_output_tokens)

    print(label)
    print(f"- Input tokens: {input_tokens}")
    print(f"- Expected output tokens: {expected_output_tokens}")
    print(f"- Estimated cost: ${estimated_cost:.6f}")
    if context_limit:
        used_percent = (input_tokens / context_limit) * 100
        print(f"- Context used: {used_percent:.2f}% of {context_limit:,} tokens")
        if used_percent > 80:
            print("- Warning: prompt is using more than 80% of the context window")
    print()


def basic_text_example() -> int:
    messages = [
        {
            "role": "user",
            "content": "Explain prompt caching to a backend engineer in 3 bullets.",
        }
    ]
    return count_tokens(messages)


def system_prompt_example() -> int:
    system = "You are a concise API tutor. Prefer concrete examples over theory."
    messages = [{"role": "user", "content": "Explain Claude tool use."}]
    return count_tokens(messages, system=system)


def tool_schema_example() -> int:
    messages = [
        {
            "role": "user",
            "content": "Look up order A123 and convert 32 C to Fahrenheit.",
        }
    ]
    return count_tokens(messages, tools=TOOLS)


def image_input_example() -> int:
    messages = [
        {
            "role": "user",
            "content": [
                image_block_from_url(
                    "https://upload.wikimedia.org/wikipedia/commons/3/3f/Fronalpstock_big.jpg"
                ),
                {"type": "text", "text": "Describe this image in one sentence."},
            ],
        }
    ]
    return count_tokens(messages)


def compare_prompt_sizes() -> None:
    print_estimate("Basic text", basic_text_example())
    print_estimate("System prompt", system_prompt_example())
    print_estimate("Tool schemas", tool_schema_example())
    print_estimate("Image input", image_input_example())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Claude token counting examples.")
    parser.add_argument(
        "mode",
        choices=["basic", "system", "tools", "image", "all"],
        help="Token counting scenario to run.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.mode == "basic":
        print_estimate("Basic text", basic_text_example())
    elif args.mode == "system":
        print_estimate("System prompt", system_prompt_example())
    elif args.mode == "tools":
        print_estimate("Tool schemas", tool_schema_example())
    elif args.mode == "image":
        print_estimate("Image input", image_input_example())
    elif args.mode == "all":
        compare_prompt_sizes()


if __name__ == "__main__":
    main()
