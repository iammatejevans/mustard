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
        response = fle.read().replace('\n', '')

        for_loop = re.findall('{%[ ]?for.+endfor[ ]?%}', response, flags=re.MULTILINE)

        while for_loop:
            # TODO: add handling for nested loops
            text_match = re.findall('{%[^}{]*%}', for_loop[0])
            text_match_first = text_match[0]
            var = text_match_first.split('for ')[1].split()[0]
            value = text_match_first.split(' in ')[1].split()[0]
            value = match_variable(value, kwargs)
            match = for_loop[0]
            match_modified = match.replace(text_match_first, '').replace(text_match[1], '')
            result = []

            for item in value:
                kwargs[var] = item
                result.append(match_variable(match_modified, kwargs))

            result = '\n'.join(result)
            response = response.replace(match, result)
            for_loop = re.findall('{%[ ]?for.+endfor[ ]?%}', response, flags=re.MULTILINE)

        while '{{' in response:
            text_match = re.findall('{{[^}{]*}}', response)[0]
            result = match_variable(text_match, kwargs)

            try:
                response = response.replace(text_match, result)
            except TypeError:
                response = response.replace(text_match, result.__str__())

        while '{%' in response:
            text_match = re.findall('{%[^}{]*%}', response)
            text_match_first = text_match[0]
            result = match_fnc(text_match_first, kwargs)
            result = eval(result)

            try:
                response = response.replace(text_match_first, result)
            except TypeError:
                response = response.replace(text_match_first, result.__str__())

        fle.close()
        return response


def match_variable(text, kwargs):
    html_start = ''
    html_end = ''

    if re.findall('.+{{', text):
        html_start = re.findall('.+{{', text)[0].replace('{{', '')
        html_end = re.findall('}}.+', text)[0].replace('}}', '')
        text = text.split('{{')[1].split('}}')[0]
    else:
        text = text.replace('{{', '').replace('}}', '')

    text = text.strip().split('.')

    if text[0] in kwargs:
        arg = kwargs[text[0]]

        for i in text[1:]:
            arg = getattr(arg, i)

        if html_start or html_end:
            return html_start + arg + html_end

        return arg
    return None


def match_fnc(text, kwargs):
    result = []
    text = text.replace('{%', '').replace('%}', '').strip()
    text = text.split()
    for word in text:
        if '.' in word:
            word = match_variable(word, kwargs)
            word = f'"{word}"' if isinstance(word, str) else word
            if isinstance(word, list):
                l = ', '.join(word)
                word = f'"[{l}"]' if isinstance(word, list) else word
        if word in kwargs:
            result.append(kwargs[word])
        else:
            result.append(word)

    try:
        result = ' '.join(result)
    except TypeError:
        result = ' '.join([word.__str__() for word in result])
    return result


if __name__ == '__main__':
    class Hello:
        meloun = 'whatever'
        true = None

    a = Hello()
    render('home.html', {'pokus': a})
