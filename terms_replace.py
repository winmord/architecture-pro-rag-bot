import os
import json
import re
from pathlib import Path

def load_terms(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    mapping = {}
    for obj in data["objects"]:
        for k, v in obj.items():
            mapping[k] = v
    return mapping

def pluralize(word):
    if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    if word.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return word + 'es'
    return word + 's'

def match_case(source, target):
    if source.isupper():
        return target.upper()
    if source.istitle():
        return target.title()
    return target

def replace_with_articles(text, src, dst):
    pattern = re.compile(r'\b(a|an|the)?\s*' + re.escape(src) + r'(s?)\b', re.IGNORECASE)

    def repl(match):
        article = match.group(1)
        plural_suffix = match.group(2)
        original = match.group(0)

        replacement = dst

        if plural_suffix:
            replacement = pluralize(replacement)

        if article:
            if article.lower() in ['a', 'an']:
                if replacement[0].lower() in 'aeiou':
                    article_fixed = 'an'
                else:
                    article_fixed = 'a'
            else:
                article_fixed = article.lower()
            replacement = article_fixed + ' ' + replacement

        replacement = match_case(original, replacement)
        return replacement

    return pattern.sub(repl, text)

def process_file(input_path, output_path, mapping):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    for src, dst in sorted(mapping.items(), key=lambda x: -len(x[0])):
        text = replace_with_articles(text, src, dst)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

def main():
    input_dir = Path('initial_pages')
    output_dir = Path('knowledge_base')
    output_dir.mkdir(parents=True, exist_ok=True)

    mapping = load_terms('terms_map.json')

    for file in input_dir.glob('*.txt'):
        output_file = output_dir / file.name
        process_file(file, output_file, mapping)

if __name__ == "__main__":
    main()