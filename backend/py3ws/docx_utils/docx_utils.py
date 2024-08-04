from docx import Document


class DocxUtils:
    def __init__(self, document: str):
        self.document = Document(document)

    def replace(self, search_str: str, replace_str: str):
        for p in self.document.paragraphs:
            if search_str in p.text:
                inline = p.runs
                # Loop added to work with runs (strings with same style)
                for i in range(len(inline)):
                    if search_str in inline[i].text:
                        text = inline[i].text.replace(search_str, replace_str)
                        inline[i].text = text

        return self.document

