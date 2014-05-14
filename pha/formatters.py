from bs4 import BeautifulSoup


def pretty_html(html_src):
    parsed_html = BeautifulSoup(html_src)
    return parsed_html.prettify()


_TOKEN_ANY = 'xxxany'
_TOKEN_OR = 'xxxor'

_PRE_PARSE_REPLACEMENTS = {
    '(': '',
    ')': '',
    '.*': _TOKEN_ANY,
    '|': _TOKEN_OR
}

_POST_PARSE_REPLACEMENTS = {
    _TOKEN_ANY: '*',
    _TOKEN_OR: '|',
    '&lt;': '<',
    '&gt;': '>'
}


def pretty_spec(spec):
    pretty_spec_html = BeautifulSoup(_build_spec_html(spec)).prettify()
    for before, after in _POST_PARSE_REPLACEMENTS.items():
        pretty_spec_html = pretty_spec_html.replace(before, after)
    return pretty_spec_html


def _build_spec_html(spec):
    element_name = spec.name_regex[1:-1]
    for before, after in _PRE_PARSE_REPLACEMENTS.items():
        element_name = element_name.replace(before, after)

    attr_string = ''
    for key, value in spec.attrs.items():
        attr_string += ' {0}="{1}"'.format(key, value)
    html_string = '<{0}{1}>'.format(element_name, attr_string)

    if spec.content:
        html_string += spec.content

    for child in spec.children:
        html_string += _build_spec_html(child)
    html_string += '</{0}>'.format(element_name)

    return html_string