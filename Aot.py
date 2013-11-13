# -*- encoding: utf-8 -*-
import codecs
import pymorphy2
from nltk.tokenize import wordpunct_tokenize


# It is strongly recommended to create only 1 instance of PyMorphy.
morph = pymorphy2.MorphAnalyzer()


def get_tokens(text):
    return [token for token in wordpunct_tokenize(text) if not pymorphy2.shapes.is_punctuation(token)]


def read_text(file_name):
    line_parts = [line.split("\t") for line in get_unicode_lines(file_name)]
    records = {}
    for parts in line_parts:
        rec_id = int(parts[0])
        records[rec_id] = parts[1]
    return records


def console_println(unicode_text):
    if isinstance(unicode_text, basestring):
        print(unicode_text.encode("utf-8") + "\n")
    else:
        print(unicode_text)
        print("\n")


def get_unicode_lines(file_name):
    with codecs.open(file_name, "r", "utf-8-sig") as f:
        return f.readlines()


def get_lemma_word(word):
    upper_word = (unicode(word)).upper()
    info = morph.parse(upper_word)
    if len(info) > 0:
        return info[0].normal_form
    return upper_word


def original_word_info(word):
    return [pymorphy2.analyzer.Parse(word=word, tag=None, normal_form=word, score=0, methods_stack=())]


def get_lemma_infos(text):
    infos = []
    for word in get_tokens(text):
        info = morph.parse(word)
        if len(info) <= 0:
            info = original_word_info(word)
        infos.append(info[0])
    return infos


def get_lemma_words(text):
    tokens = get_tokens(text)
    for token in tokens:
        yield get_lemma_word(token)


def get_lemma_text(text):
    return " ".join(get_lemma_words(text))


def get_pos_tag(lemma_info):
    if lemma_info.tag is None:
        return ""
    return lemma_info.tag.POS