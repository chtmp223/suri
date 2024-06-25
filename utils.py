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
    separators = [".", "?", "!", "\n"]
    last_separator_index = -1

    # Find the last punctuation mark that ends a sentence.
    for sep in separators:
        index = text.rfind(sep)
        if index > last_separator_index:
            last_separator_index = index

    # Check if the last sentence is shorter than 30 words.
    if last_separator_index != -1:
        last_sentence = text[last_separator_index + 1 :].strip()
        if len(last_sentence.split()) < 30:
            return text[: last_separator_index + 1]
        else:
            return text
    else:
        return text
    

def truncating_words(document, max_tokens):
    """
    Truncating the document down to contain only max_tokens
    """
    lines = document.split("\n")
    word_count = 0
    truncated_document = []

    for line in lines:
        words_in_line = line.split()
        for word in words_in_line:
            if word_count < max_tokens:
                truncated_document.append(word)
                word_count += 1
            else:
                break
        if word_count >= max_tokens:
            break
        truncated_document.append("\n")

    return " ".join(truncated_document).strip()
