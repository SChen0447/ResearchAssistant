from langchain_pymupdf4llm import PyMuPDF4LLMLoader


def load_pdf_data(data_path):
    loader = PyMuPDF4LLMLoader(file_path=data_path)
    return loader.load()

