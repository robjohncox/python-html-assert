import logging
import re
from bs4 import BeautifulSoup
from bs4.element import Tag

log = logging.getLogger('pha')


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

    # TODO This should return a proper results object that
    #  - Wraps up the match/not match result
    #  - Contains information required to debug the matching process
    #  - Allows the client to easily print information to help with debugging failures

    def matches(self, element):
        if self._name_matches(element)\
                and self._content_matches(element)\
                and self._attributes_match(element)\
                and self._children_match(element):
            log.info('Match found: {0} on element {1}'.format(str(self), element.name))
            return True
        return self._search_children_for_match(element)

    def _name_matches(self, element):
        return self.name_matcher.match(element.name)

    def _content_matches(self, element):
        if not self.content:
            return True
        return element.string and self.content in element.string

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

    # TODO Move __repr__ into an as_html method and build a proper __repr__ impl

    def __repr__(self):
        element_name = self.name_regex[1:-1].replace('(', '').replace(')', '').replace('.*', 'xxxany').replace('|', 'xxxor')
        attr_string = ''
        for key, value in self.attrs.items():
            attr_string += ' {0}="{1}"'.format(key, value)
        html_string = '<{0}{1}>'.format(element_name, attr_string)
        if self.content:
            html_string += self.content
        for child in self.children:
            html_string += repr(child)
        html_string += '</{0}>'.format(element_name)
        return html_string

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


# TODO Move this to an as_html method on the element matchers


def pretty_spec(spec):
    spec_as_html = BeautifulSoup(repr(spec))
    return spec_as_html.prettify().replace('xxxany', '*').replace('&lt;', '<').replace('&gt;', '>').replace('xxxor', '|')


def pretty_html(html_src):
    parsed_html = BeautifulSoup(html_src)
    return parsed_html.prettify()