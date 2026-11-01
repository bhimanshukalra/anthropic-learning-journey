from datetime import datetime
from devtools import debug

from dotenv import load_dotenv
from google import genai
import instructor
from pydantic import BaseModel, field_validator
from pypdf import PdfReader

load_dotenv()


class InvoiceData(BaseModel):
    vendor: str
    invoice_date: datetime
    due_date: datetime
    invoice_number: str
    total_due: str

    @field_validator("invoice_date", "due_date", mode="before")
    @classmethod
    def parse_dates(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


def pdf_to_text(file_path):
    reader = PdfReader(file_path)
    all_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"

    return all_text.strip()


text = pdf_to_text("data/invoice-sample.pdf")

client = instructor.from_genai(
    genai.Client(),
    mode=instructor.Mode.GENAI_TOOLS,
)

invoice_data = client.chat.completions.create(
    model="gemini-2.5-flash",
    response_model=InvoiceData,
    messages=[
        {
            "role": "user",
            "content": f"Extract the invoice details from this text:\n\n{text}",
        }
    ],
)

debug(invoice_data)
