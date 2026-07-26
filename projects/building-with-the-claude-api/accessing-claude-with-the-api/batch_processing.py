import argparse
import time
from typing import Any

from claude_helpers import CLAUDE_MODEL, client, extract_text

POLL_INTERVAL_SECONDS = 5


def build_batch_requests() -> list[dict[str, Any]]:
    prompts = [
        "Classify this feedback as bug, feature_request, or praise: The export button crashes.",
        "Classify this feedback as bug, feature_request, or praise: Please add dark mode.",
        "Classify this feedback as bug, feature_request, or praise: The app is fast and clear.",
    ]

    return [
        {
            "custom_id": f"feedback-{index}",
            "params": {
                "model": CLAUDE_MODEL,
                "max_tokens": 80,
                "messages": [{"role": "user", "content": prompt}],
            },
        }
        for index, prompt in enumerate(prompts, start=1)
    ]


def create_batch() -> Any:
    # Batch requests are best for offline work where lower cost matters more
    # than immediate latency, such as evals or bulk document processing.
    return client.messages.batches.create(requests=build_batch_requests())


def retrieve_batch(batch_id: str) -> Any:
    return client.messages.batches.retrieve(batch_id)


def wait_for_batch(batch_id: str) -> Any:
    while True:
        batch = retrieve_batch(batch_id)
        print(f"Batch {batch.id}: {batch.processing_status}")

        if batch.processing_status == "ended":
            return batch

        time.sleep(POLL_INTERVAL_SECONDS)


def print_batch_summary(batch: Any) -> None:
    print("Batch summary:")
    print(f"- ID: {batch.id}")
    print(f"- Status: {batch.processing_status}")
    print(f"- Created at: {batch.created_at}")
    print(f"- Expires at: {batch.expires_at}")
    print(f"- Ended at: {batch.ended_at}")
    print(f"- Request counts: {batch.request_counts}")
    print()


def print_batch_results(batch_id: str) -> None:
    # Results are streamed as JSONL by the SDK. Each item maps back to the
    # original request using custom_id.
    for result in client.messages.batches.results(batch_id):
        print(f"Result for {result.custom_id}: {result.result.type}")

        if result.result.type == "succeeded":
            message = result.result.message
            print(extract_text(message))
        elif result.result.type == "errored":
            print(result.result.error)
        elif result.result.type == "expired":
            print("Request expired before processing.")
        elif result.result.type == "canceled":
            print("Request was canceled.")

        print()


def create_and_print_id() -> None:
    batch = create_batch()
    print_batch_summary(batch)
    print("Save this batch ID for later:")
    print(batch.id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Claude Message Batches examples.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("create", help="Create a new message batch.")

    retrieve = subparsers.add_parser("retrieve", help="Retrieve batch status.")
    retrieve.add_argument("batch_id")

    wait = subparsers.add_parser("wait", help="Poll until the batch ends.")
    wait.add_argument("batch_id")

    results = subparsers.add_parser("results", help="Print batch results.")
    results.add_argument("batch_id")

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "create":
        create_and_print_id()
    elif args.command == "retrieve":
        print_batch_summary(retrieve_batch(args.batch_id))
    elif args.command == "wait":
        print_batch_summary(wait_for_batch(args.batch_id))
    elif args.command == "results":
        print_batch_results(args.batch_id)


if __name__ == "__main__":
    main()
