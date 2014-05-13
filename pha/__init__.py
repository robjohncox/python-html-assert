import re
from bs4 import BeautifulSoup
from bs4.element import Tag


# TODO Separate out bootstrap specific helpers into a plugin module


class ElementMatcher(object):

    def __init__(self, name_regex, *children, **attrs):
        self.name_regex = name_regex
        self.name_matcher = re.compile(name_regex)
        self.children = [child for child in children if child]
        self.attrs = attrs

        self.content = self._keyword_attr('content')
        
    def _keyword_attr(self, attr_name):
        if attr_name in self.attrs:
            attr_value = self.attrs[attr_name]
            del self.attrs[attr_name]
        else:
            attr_value = None
        return attr_value

    def matches(self, element):
        if self._name_matches(element)\
                and self._content_matches(element)\
                and self._attributes_match(element)\
                and self._children_match(element):
            return True
        return self._search_children_for_match(element)

    def _name_matches(self, element):
        return self.name_matcher.match(element.name)

    def _content_matches(self, element):
        if not self.content:
            return True
        return self.content in element.string

    def _attributes_match(self, element):
        for key, value in self.attrs.items():
            if key not in element.attrs or value not in element.attrs[key]:
                return False
        return True

    def _children_match(self, element):
        if not self.children:
            return True

        child_index = 0
        for element_child in [child for child in element.children if type(child) is Tag]:
            if self.children[child_index].matches(element_child):
                child_index += 1
            if child_index == len(self.children):
                return True
        return False

    def _search_children_for_match(self, element):
        for child_element in [child for child in element.children if type(child) is Tag]:
            if self.matches(child_element):
                return True
        return False

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return 'ElementMatcher[name_regex={0},content={1}]'.format(self.name_regex, self.content)


def html_matches(spec, content):
    parsed_html = BeautifulSoup(content)
    return spec.matches(parsed_html)


def elem(name, *children, **attrs):
    elem_regex = r'^{0}$'.format(name)
    return ElementMatcher(elem_regex, None, *children, **attrs)


def html(*children, **attrs):
    return ElementMatcher(r'^html$', None, *children, **attrs)


def heading(heading_text, *children, **attrs):
    attrs['content'] = heading_text
    return ElementMatcher(r'^(h1|h2|h3|h4|h5|h6)$', *children, **attrs)


def text(text_content, *children, **attrs):
    attrs['content'] = text_content
    return ElementMatcher(r'^.*$', *children, **attrs)


def a(href=None, link_text=None, *children, **attrs):
    if href:
        attrs['href'] = href
    if link_text:
        attrs['content'] = link_text
    return ElementMatcher(r'^a$', *children, **attrs)


def accordion(*children, **attrs):
    attrs['class'] = 'accordion'
    return ElementMatcher(r'^div$', *children, **attrs)


def acc_group(*children, **attrs):
    attrs['class'] = 'accordion-group'
    return ElementMatcher(r'^div$', *children, **attrs)


def acc_heading(*children, **attrs):
    attrs['class'] = 'accordion-heading'
    return ElementMatcher(r'^div$', *children, **attrs)


def acc_body(*children, **attrs):
    attrs['class'] = 'accordion-body'
    return ElementMatcher(r'^div$', *children, **attrs)