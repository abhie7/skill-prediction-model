import re
from pdfminer.high_level import extract_text

class PdfParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_cleaned_text(self):
        text = extract_text(self.filepath)
        cleaned_text = self.clean_text(text)
        return cleaned_text

    @staticmethod
    def clean_text(text):
        text = re.sub(r"\n+", " ", text)  # replaces multiple newlines with a space
        text = re.sub(r"[^\w\s/#@._+\-/\\-]", ' ', text)  # removes special characters except word characters, spaces, @, /, \, and -
        text = re.sub(r"\s{2,}", " ", text)  # replaces multiple spaces with a single space
        text = re.sub(r"[•\t▪➢❖]", '', text)  # removes specific bullet points and characters
        text = text.strip()
        return text.lower()

if __name__ == '__main__':
    pdf_filepath = r'test_resumes/54665_Manjunath_S.pdf'
    parser = PdfParser(pdf_filepath)
    cleaned_text = parser.get_cleaned_text()
    print('\n', cleaned_text)