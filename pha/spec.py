import re


class ElementDef(object):

    def __init__(self, name_regex, *children, **attrs):
        self.name_regex = name_regex
        self.name_matcher = re.compile(name_regex)
        self.children = [child for child in children if child]
        self.attrs = attrs

        self._handle_escaped_attrs()
        self.content = self._keyword_attr('content')

    def _handle_escaped_attrs(self):
        attrs_to_replace = list()
        for key, value in self.attrs.items():
            if key.endswith('_'):
                self.attrs[key.replace('_', '')] = value
                attrs_to_replace.append(key)

        for key in attrs_to_replace:
            del self.attrs[key]

    def _keyword_attr(self, attr_name):
        if attr_name in self.attrs:
            attr_value = self.attrs[attr_name]
            del self.attrs[attr_name]
        else:
            attr_value = None
        return attr_value

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return 'ElementMatcher[name_regex={0},content={1},attrs={2}]'.format(self.name_regex, self.content, self.attrs)


def elem(name, *children, **attrs):
    elem_regex = r'^{0}$'.format(name)
    return ElementDef(elem_regex, None, *children, **attrs)


def html(*children, **attrs):
    return ElementDef(r'^html$', None, *children, **attrs)


def heading(heading_text, *children, **attrs):
    attrs['content'] = heading_text
    return ElementDef(r'^(h1|h2|h3|h4|h5|h6)$', *children, **attrs)


def text(text_content, *children, **attrs):
    attrs['content'] = text_content
    return ElementDef(r'^.*$', *children, **attrs)


def a(href=None, link_text=None, *children, **attrs):
    if href:
        attrs['href'] = href
    if link_text:
        attrs['content'] = link_text
    return ElementDef(r'^a$', *children, **attrs)


def accordion(*children, **attrs):
    attrs['class_'] = 'accordion'
    return div(*children, **attrs)


def acc_group(*children, **attrs):
    attrs['class_'] = 'accordion-group'
    return div(*children, **attrs)


def acc_heading(*children, **attrs):
    attrs['class_'] = 'accordion-heading'
    return div(*children, **attrs)


def acc_body(*children, **attrs):
    attrs['class_'] = 'accordion-body'
    return div(*children, **attrs)


def div(*children, **attrs):
    return ElementDef(r'^div$', *children, **attrs)