import os
import re

try:
    import settings as settings
except ImportError:
    import default_settings as settings


def render(template: str, kwargs: dict = None):
    if not kwargs:
        kwargs = {}

    directory = os.path.join(settings.TEMPLATE_DIR, template)

    if os.path.exists(directory):
        fle = open(directory, 'r')
        response = ' '.join(fle.read().split())
        response = response.replace('\n', '')
        response = response.replace('{{ ', '{{').replace(' }}', '}}').replace('{% ', '{%').replace(' %}', '%}')

        for_loop = re.findall('{%for.+endfor%}', response, flags=re.MULTILINE)
        dict_loop = re.findall('{%for[^{]*%}', for_loop[0], flags=re.MULTILINE)
        if dict_loop:
            response = dict_loop_handler(re.search('({%for)((?!{%).)*{%endfor%}', for_loop[0]).group(), response,
                                         kwargs)
        for_loop = re.findall('{%for.+endfor%}', response, flags=re.MULTILINE)
        while for_loop:
            response, _ = loop_handler(for_loop, response, kwargs)
            for_loop = re.findall('{%for.+endfor%}', response, flags=re.MULTILINE)

        while '{{' in response:
            text_match = re.findall('{{[^}{]*}}', response)[0]
            result = variable_handler(text_match, kwargs)

            try:
                response = response.replace(text_match, result)
            except TypeError:
                response = response.replace(text_match, result.__str__())

        while '{%' in response:
            text_match = re.findall('{%[^}{]*%}', response)
            text_match_first = text_match[0]
            result = fnc_handler(text_match_first, kwargs)
            result = eval(result) if result else ''

            try:
                response = response.replace(text_match_first, result)
            except TypeError:
                response = response.replace(text_match_first, result.__str__())

        fle.close()
        return response


def dict_loop_handler(dict_loop, response, kwargs):
    result = []
    start = re.findall('{%for[^{]*%}', dict_loop, flags=re.MULTILINE)[0]
    dict_key = start.split('%}')[0].split('for ')[1].split(',')[0].strip()
    dict_value = start.split('%}')[0].split('for ')[1].split(',')[1].strip().split()[0]
    dictionary = start.split('%}')[0].split(' in ')[1].strip().split()[0].split('.')[0]
    dictionary = variable_handler(dictionary, kwargs)

    text = dict_loop.replace(re.findall('{%for[^{]*%}', dict_loop)[0], '')
    text = text.replace(re.findall('{%endfor%}', text)[-1], '')

    for key, value in dictionary.items():
        kwargs[dict_key] = key
        kwargs[dict_value] = value
        loop_text = text

        for i in range(len(re.findall('{{[^{]+}}', loop_text))):
            item = re.findall('{{[^{]+}}', text)[i]
            new_item = variable_handler(item, kwargs)
            loop_text = loop_text.replace(item, new_item)

        result.append(loop_text)

    response = response.replace(text, ' '.join(result))
    response = response.replace(start, '').replace(re.findall('{%endfor%}', dict_loop)[0], '', 1)

    return response


def loop_handler(for_loop, response, kwargs):
    loop = '%}'.join(for_loop[0].split('%}')[1:])
    loop = '{%'.join(loop.split('{%')[:-1])
    nested_loop = re.findall('{%for.+endfor%}', loop, flags=re.MULTILINE)

    if nested_loop:
        response, for_loop = loop_handler(nested_loop, response, kwargs)

    text_match = re.findall('{%[^}{]*%}', for_loop[0])
    text_match_first = text_match[0]
    var = text_match_first.replace('{%', '').replace('%}', '').split('for ')[1].split()[0]
    value_original = text_match_first.replace('{%', '').replace('%}', '').split(' in ')[1].split()[0]
    value = variable_handler(value_original, kwargs)
    match = for_loop[0]
    match_modified = match.replace(text_match_first, '').replace(text_match[-1], '')
    result = []

    for i in range(len(value)):
        word = match_modified.replace(('{{' + var + '}}'), '{{' + f'{value_original}[{i}]' + '}}')
        result.append(word)

    result = ' '.join(result)
    response = response.replace(match, result)
    for_loop = re.findall('{%for.+endfor%}', response, flags=re.MULTILINE)

    return response, for_loop


def slicing_handler(text: str, kwargs: dict, arg=None):
    if re.findall('[\d+]', text):
        index: int = int(text.split('[')[1].replace(']', ''))
        if text.split('[')[0] in kwargs:
            arg = kwargs[text.split('[')[0]]
            arg = arg[index]
            return arg
        if arg:
            arg = getattr(arg, text.split('[')[0])[int(index)]
            return arg
    return None


def variable_handler(text: str, kwargs: dict):
    text = text.replace('{{', '').replace('}}', '')
    text = text.strip().split('.')
    arg = slicing_handler(text[0], kwargs)

    if text[0] in kwargs:
        arg = kwargs[text[0]]

    if arg:
        for i in text[1:]:
            arg = slicing_handler(i, kwargs, arg) if slicing_handler(i, kwargs, arg) else getattr(arg, i)
        return arg
    return None


def fnc_handler(text, kwargs):
    result = []
    text = text.replace('{%', '').replace('%}', '').strip()
    text = text.split()

    for word in text:
        if '.' in word:
            word = f'"{variable_handler(word, kwargs)}"'
        elif re.findall('[\d+]', word.__str__()):
            word = slicing_handler(word, kwargs)

        if word in kwargs:
            result.append(f'"{kwargs[word]}"')
        else:
            result.append(word)

    result = ' '.join(result)
    return result


if __name__ == '__main__':
    pass
