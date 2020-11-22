from os import path
import re
import numpy as np


def back_permutation(p: list):
    op: list = [0 for _ in p]
    for i in range(len(p)):
        op[p[i]] = i
    return op


def encrypt(text: str, keyword: str) -> str:
    matrix = np.array(list([char for char in text]))
    text_len: int = len(text)
    width: int = len(keyword)
    height: int = text_len // width
    if width * height < text_len:
        height += 1
        matrix = np.concatenate([matrix, [' ' for _ in range(width * height - text_len)]])
    matrix = np.transpose(matrix.reshape(width, height))
    permutation = sorted(range(width), key=lambda k: keyword[k])
    idx = np.empty_like(permutation)
    idx[permutation] = np.arange(len(permutation))
    matrix[:] = matrix[:, idx]
    return ''.join(matrix.flatten())


def decrypt(text: str, keyword: str) -> str:
    matrix = np.array(list([char for char in text]))
    text_len: int = len(text)
    width: int = len(keyword)
    height: int = text_len // width
    if width * height != text_len:
        raise ValueError('Wrong keyword')
    matrix = matrix.reshape(height, width)
    permutation = back_permutation(sorted(range(width), key=lambda k: keyword[k]))
    idx = np.empty_like(permutation)
    idx[permutation] = np.arange(len(permutation))
    matrix[:] = matrix[:, idx]
    return ''.join(np.transpose(matrix).flatten())


def strip_text(text: str) -> str:
    text: str = text.lower().strip()
    text: str = re.sub(r'[.,/#!$%^&*;:{}=\-_`~()@<>\[\]"?\\\n]', '', text)
    text: str = re.sub(r'(\s)\s+', r'\1', text)
    return text


def add_postfix_to_file(filepath: str, postfix: str) -> str:
    filename: str = path.split(filepath)[-1]
    filename_comps: list = filename.split('.')
    if len(filename_comps) == 1:
        output_filename: str = f'{filename}{postfix}'
    else:
        ext: str = filename_comps[-1]
        filename: str = '.'.join(filename_comps[:-1])
        output_filename: str = f'{filename}{postfix}.{ext}'

    filepath: str = path.join(*path.split(filepath)[:-1])
    return path.join(filepath, output_filename)


def encrypt_file(filepath: str, keyword: str):
    text: str
    with open(filepath, 'r') as file:
        text: str = ''.join(file.readlines())
    text: str = strip_text(text)
    encrypted_text: str = encrypt(text, keyword)

    output_filename: str = add_postfix_to_file(filepath, '_encrypted')

    with open(output_filename, 'w') as output:
        output.write(encrypted_text)


def decrypt_file(filepath: str, keyword: str):
    text: str
    with open(filepath, 'r') as file:
        text: str = ''.join(file.readlines())
    decrypted_text: str = decrypt(text, keyword)

    output_filename: str = filepath.replace('_encrypted', '_decrypted')

    with open(output_filename, 'w') as output:
        output.write(decrypted_text)
