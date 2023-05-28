import os


def get_violation_type(violation: dict) -> str:
    return violation["source"].split(".")[-1][:-5]


def load_file(file_path):
    """
    Opens the file and reads its content
    """
    content = None
    if file_path:
        try:
            with open(file_path, 'r+', encoding='utf-8') as file:
                content = file.read()
        except Exception as err:
            try:
                with open(file_path, 'r+', encoding='ISO-8859-1') as file:
                    content = file.read()
            except Exception as err2:
                pass
    return content


def save_file(content, file_path):
    """
    Writes the content in a file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as err:
        try:
            with open(file_path, 'w', encoding='ISO-8859-1') as file:
                file.write(content)
        except Exception as err2:
            return None
    return file_path