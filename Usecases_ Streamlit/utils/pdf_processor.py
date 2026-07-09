"""
PDF processing utilities for document analysis
"""

import base64
import fitz  # PyMuPDF
from utils.config import PDF_DPI, BASE_DPI, IMAGE_FORMAT, MEDIA_TYPE


def convert_pdf_to_images(pdf_document, max_pages):
    """
    Convert PDF pages to base64-encoded images

    Args:
        pdf_document: PyMuPDF document object
        max_pages (int): Maximum number of pages to process

    Returns:
        list: List of base64-encoded image strings
    """
    page_images = []
    num_pages = min(len(pdf_document), max_pages)

    for page_num in range(num_pages):
        page = pdf_document[page_num]

        # Convert page to image with specified DPI
        matrix = fitz.Matrix(PDF_DPI / BASE_DPI, PDF_DPI / BASE_DPI)
        pix = page.get_pixmap(matrix=matrix)
        img_data = pix.tobytes(IMAGE_FORMAT)

        # Convert to base64
        img_base64 = base64.b64encode(img_data).decode("utf-8")
        page_images.append(img_base64)

    return page_images


def prepare_content_for_claude(page_images, prompt):
    """
    Prepare content array for Claude API with images and prompt

    Args:
        page_images (list): List of base64-encoded images
        prompt (str): Text prompt for analysis

    Returns:
        list: Formatted content array for Claude API
    """
    content = []

    # Add each page as an image with separators
    for i, img_base64 in enumerate(page_images):
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": MEDIA_TYPE,
                    "data": img_base64,
                },
            }
        )

        # Add separator between pages (except after last page)
        if i < len(page_images) - 1:
            content.append({"type": "text", "text": f"--- End of Page {i + 1} ---"})

    # Add main prompt
    content.append(
        {
            "type": "text",
            "text": f"{prompt}\n\nThis PDF contains {len(page_images)} page(s). Please analyse all the content shown.",
        }
    )

    return content
