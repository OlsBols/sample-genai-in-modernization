import fitz
import pandas as pd
import os
from utils.config import FILE_PATHS, FILE_LIMITS


def validate_file_size(uploaded_file):
    """
    Validate uploaded file size against FILE_LIMITS

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not uploaded_file:
        return False, "No file uploaded"

    max_size_bytes = FILE_LIMITS["max_size_mb"] * 1024 * 1024
    file_size = len(uploaded_file.getvalue())

    if file_size > max_size_bytes:
        return (
            False,
            f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds limit ({FILE_LIMITS['max_size_mb']}MB)",
        )

    return True, "File size is valid"


def process_pdf_bytes(uploaded_file):
    """
    Convert Streamlit uploaded file to PyMuPDF document

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        fitz.Document: PyMuPDF document object
    """
    pdf_bytes = uploaded_file.getvalue()
    return fitz.open(stream=pdf_bytes, filetype="pdf")


def get_file_path(file_key: str) -> str:
    """
    Get file path for specified CSV data file

    Args:
        file_key (str): Key for the required file path

    Returns:
        str: Full file path for the CSV file

    Raises:
        KeyError: If file_key is not found in FILE_PATHS
    """
    if file_key not in FILE_PATHS:
        raise KeyError(f"File path key '{file_key}' not found in configuration")
    return FILE_PATHS[file_key]


def read_csv_file(file_key):
    """
    Read CSV file using configured file paths

    Args:
        file_key (str): Key for the CSV file in FILE_PATHS configuration
        **kwargs: Additional arguments to pass to pandas.read_csv()

    Returns:
        Optional[pd.DataFrame]: DataFrame containing CSV data, None if error occurs
    """
    try:
        file_path = get_file_path(file_key)
        if not os.path.exists(file_path):
            print(f"WARNING: CSV file not found at path: {file_path}")
            return None

        df = pd.read_csv(file_path)
        print(f"Successfully loaded CSV file: {file_path} ({len(df)} rows)")
        return df
    except FileNotFoundError:
        print(f"ERROR: CSV file not found for key '{file_key}'")
        return None
    except pd.errors.EmptyDataError:
        print(f"ERROR: CSV file is empty for key '{file_key}'")
        return None
    except Exception as e:
        print(f"ERROR: Failed to read CSV file for key '{file_key}'. Reason: {e}")
        return None
