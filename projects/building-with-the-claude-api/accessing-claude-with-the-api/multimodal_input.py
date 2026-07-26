import argparse
import base64
import math
import mimetypes
from pathlib import Path
from typing import Any

from claude_helpers import CLAUDE_MODEL, client, extract_text, print_message_metadata

DEFAULT_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/3/3f/Fronalpstock_big.jpg"
DEFAULT_PDF_URL = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"

SUPPORTED_IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def encode_file(path: Path) -> str:
    # Local files must be base64-encoded before they can be embedded in a request.
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


def guess_image_media_type(path: Path) -> str:
    media_type = SUPPORTED_IMAGE_TYPES.get(path.suffix.lower())
    if media_type:
        return media_type

    guessed_type, _ = mimetypes.guess_type(path)
    if guessed_type in SUPPORTED_IMAGE_TYPES.values():
        return guessed_type

    supported = ", ".join(sorted(SUPPORTED_IMAGE_TYPES))
    raise ValueError(f"Unsupported image type for {path}. Supported extensions: {supported}")


def image_block_from_path(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    return {
        "type": "image",
        "source": {
            # Base64 is useful for local files, generated assets, and private media.
            "type": "base64",
            "media_type": guess_image_media_type(path),
            "data": encode_file(path),
        },
    }


def image_block_from_url(url: str) -> dict[str, Any]:
    return {
        "type": "image",
        "source": {
            # URL sources keep the request body small when the media is public.
            "type": "url",
            "url": url,
        },
    }


def pdf_document_block_from_path(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported by this local document example.")

    return {
        "type": "document",
        "source": {
            # PDFs use document blocks rather than image blocks.
            "type": "base64",
            "media_type": "application/pdf",
            "data": encode_file(path),
        },
    }


def pdf_document_block_from_url(url: str) -> dict[str, Any]:
    return {
        "type": "document",
        "source": {
            "type": "url",
            "url": url,
        },
    }


def estimate_image_visual_tokens(width: int, height: int) -> int:
    # Claude prices images as 28x28 visual-token patches before model resizing.
    return math.ceil(width / 28) * math.ceil(height / 28)


def send_multimodal_message(content_blocks: list[dict[str, Any]], *, max_tokens: int = 500) -> Any:
    # A multimodal prompt is still one user message; its content is a list of
    # typed blocks such as image, document, and text.
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": content_blocks}],
    )
    return message


def analyze_image(image_block: dict[str, Any]) -> Any:
    # Put images before the text prompt so Claude sees visual context first.
    return send_multimodal_message(
        [
            image_block,
            {
                "type": "text",
                "text": "Describe this image in 3 bullet points. Mention visible text if any.",
            },
        ]
    )


def compare_two_images(first_image: dict[str, Any], second_image: dict[str, Any]) -> Any:
    return send_multimodal_message(
        [
            {"type": "text", "text": "Image 1:"},
            first_image,
            {"type": "text", "text": "Image 2:"},
            second_image,
            {"type": "text", "text": "Compare these images. Focus on concrete visual differences."},
        ]
    )


def analyze_pdf(document_block: dict[str, Any]) -> Any:
    # PDFs are document blocks. Claude can use both extracted text and page images.
    return send_multimodal_message(
        [
            document_block,
            {
                "type": "text",
                "text": "Summarize the key findings in this document in 5 bullets.",
            },
        ],
        max_tokens=700,
    )


def upload_file_for_reuse(path: Path, media_type: str) -> str:
    # Files API is useful when the same image/PDF will be reused across requests.
    # You send the bytes once, then refer to the returned file_id later.
    with path.open("rb") as file_handle:
        uploaded = client.beta.files.upload(file=(path.name, file_handle, media_type))
    return uploaded.id


def image_block_from_file_id(file_id: str) -> dict[str, Any]:
    return {
        "type": "image",
        "source": {"type": "file", "file_id": file_id},
    }


def pdf_document_block_from_file_id(file_id: str) -> dict[str, Any]:
    return {
        "type": "document",
        "source": {"type": "file", "file_id": file_id},
    }


def print_response(message: Any) -> None:
    print("Response:")
    print(extract_text(message))
    print_message_metadata(message)


def build_parser() -> argparse.ArgumentParser:
    # Subcommands keep each multimodal shape isolated while sharing one script.
    parser = argparse.ArgumentParser(description="Claude multimodal input examples.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    image_url = subparsers.add_parser("image-url", help="Analyze an image from a URL.")
    image_url.add_argument("--url", default=DEFAULT_IMAGE_URL)

    image_file = subparsers.add_parser("image-file", help="Analyze a local image as base64.")
    image_file.add_argument("path", type=Path)

    pdf_url = subparsers.add_parser("pdf-url", help="Analyze a PDF from a URL.")
    pdf_url.add_argument("--url", default=DEFAULT_PDF_URL)

    pdf_file = subparsers.add_parser("pdf-file", help="Analyze a local PDF as base64.")
    pdf_file.add_argument("path", type=Path)

    upload = subparsers.add_parser("upload-file", help="Upload an image or PDF with the Files API.")
    upload.add_argument("path", type=Path)

    tokens = subparsers.add_parser("estimate-image-tokens", help="Estimate visual tokens for an image size.")
    tokens.add_argument("width", type=int)
    tokens.add_argument("height", type=int)

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "image-url":
        print_response(analyze_image(image_block_from_url(args.url)))
    elif args.command == "image-file":
        print_response(analyze_image(image_block_from_path(args.path)))
    elif args.command == "pdf-url":
        print_response(analyze_pdf(pdf_document_block_from_url(args.url)))
    elif args.command == "pdf-file":
        print_response(analyze_pdf(pdf_document_block_from_path(args.path)))
    elif args.command == "upload-file":
        path = args.path
        media_type = "application/pdf" if path.suffix.lower() == ".pdf" else guess_image_media_type(path)
        file_id = upload_file_for_reuse(path, media_type)
        print(f"Uploaded {path.name}: {file_id}")
    elif args.command == "estimate-image-tokens":
        token_count = estimate_image_visual_tokens(args.width, args.height)
        print(f"Estimated visual tokens: {token_count}")


if __name__ == "__main__":
    main()
