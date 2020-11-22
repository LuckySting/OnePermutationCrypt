import re

import enchant

eng_dict = enchant.Dict("en_US")


def check_text(text: str) -> int:
    errors: int = 0
    for word in text.split():
        if not eng_dict.check(word):
            errors += 1
            print(word)
    return errors


def strip_text(text: str) -> str:
    text: str = text.lower().strip()
    text: str = re.sub(r'[.,/#!$%^&*;:{}=\-_`~()@<>\[\]"?\\\n]', '', text)
    text: str = re.sub(r'(\s)\s+', r'\1', text)
    return text


with open('huge_text.txt', 'r') as file:
    text: str = check_text(strip_text(''.join(file.readlines())))
    print(text)
