import fitz

def read_file(file_path: str) -> dict:
    try:
        doc = fitz.open(file_path)
        doc_text = " ".join([page.get_text() for page in doc])
        return {"status": "success", "text": doc_text}
    except fitz.FitzError as e:
        return {"status": "error", "error_message": str(e)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


