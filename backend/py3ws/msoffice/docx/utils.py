import pprint


def docx_replace(doc_obj, search_str, replace_str):
    for p in doc_obj.paragraphs:
        if search_str:
            inline = p.runs
            for i in range(len(inline)):
                pprint.pprint(inline[i].text)
                if inline[i].text.find(search_str) != -1:
                    # Loop added to work with runs (strings with same style)
                    text = inline[i].text.replace(search_str, replace_str)
                    inline[i].text = text

    for table in doc_obj.tables:
        for row in table.rows:
            for cell in row.cells:
                docx_replace(cell, search_str, replace_str)


def docx_replace_regex(doc_obj, regex, replace):
    for p in doc_obj.paragraphs:
        if regex.search(p.text):
            inline = p.runs
            # Loop added to work with runs (strings with same style)
            for i in range(len(inline)):
                if regex.search(inline[i].text):
                    text = regex.sub(replace, inline[i].text)
                    inline[i].text = text

    for table in doc_obj.tables:
        for row in table.rows:
            for cell in row.cells:
                docx_replace_regex(cell, regex, replace)
