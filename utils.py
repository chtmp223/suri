import re


def check_bib(text):
    """
    Check if a text is a bibliography
    - Count("see also")>=1
    - Count("ibid")>=3
    """
    return (
        len((re.findall("see also", text.lower()))) >= 1
        or len((re.findall("ibid", text.lower()))) >= 1
    )


def strip_trailing_text(text):
    """
    Strip trailing text after the last sentence.
    If the trailing text contains more than 20 words, do not remove it.
    """
    separators = [".", "?", "!"]
    last_separator_index = -1

    # Find the last punctuation mark that ends a sentence.
    for sep in separators:
        index = text.rfind(sep)
        if index > last_separator_index:
            last_separator_index = index

    # Check if the last sentence is shorter than 20 words.
    if last_separator_index != -1:
        last_sentence = text[last_separator_index + 1 :].strip()
        if len(last_sentence.split()) < 20:
            return text[: last_separator_index + 1]
        else:
            return text
    else:
        return text
