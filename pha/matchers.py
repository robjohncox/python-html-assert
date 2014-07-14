from bs4 import BeautifulSoup
from bs4.element import Tag

from .formatters import pretty_html, pretty_spec


class MatcherResult(object):
    """ Pass/fail result for an attempted match, along with debugging information. """

    def __init__(self, spec, html_src, root_element, passed=True, element_defs_not_found=None, failed_on_def=None):
        self.spec = spec
        self.html_src = html_src
        self.root_element = root_element
        self.passed = passed
        self.element_defs_not_found = [] if not element_defs_not_found else element_defs_not_found
        self.failed_on_def = failed_on_def

    @property
    def failed(self):
        return not self.passed

    @property
    def result_text(self):
        return 'Passed' if self.passed else 'Failed'

    def pretty_spec(self):
        return pretty_spec(self.spec)

    def pretty_html_src(self):
        return pretty_html(self.html_src)

    def __repr__(self):
        return 'MatcherResult[passed={0},elem_defs_not_found={1},failed_on_def={2}'.format(self.passed,
                                                                                           self.element_defs_not_found,
                                                                                           self.failed_on_def)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        result = u'HTML Matching: {0}\n\n'.format(self.result_text.upper())

        if self.failed:
            if self.failed_on_def:
                result += u'Failed when attempting to match against {0}\n'.format(unicode(self.failed_on_def))
            if self.element_defs_not_found:
                result += u'Some element definitions were not found anywhere in the HTML:\n'
                for element_def in self.element_defs_not_found:
                    result += u' - {0}\n'.format(unicode(element_def))
            result += u'\n'

            result += u'Specification:\n{0}\n\n'.format(self.pretty_spec())
            result += u'Pruned HTML Source:\n{0}\n\n'.format(self.root_element.prettify())
            result += u'Full HTML Source:\n{0}\n\n'.format(self.pretty_html_src())

        return result


def linear_match(spec, html_src):
    """ Flattens the html and the spec, and check all spec elements appear in order. """

    root_element = BeautifulSoup(html_src)
    all_element_definitions = _flatten_element_definitions(spec)
    _prune_unmatched_elements(root_element, all_element_definitions)

    element_def_index = 0
    current_element_def = None
    for element in _descendant_elements(root_element):
        current_element_def = all_element_definitions[element_def_index]
        if _matches(current_element_def, element):
            element_def_index += 1
            if element_def_index == len(all_element_definitions):
                return MatcherResult(spec, html_src, root_element, passed=True)

    # We didn't match everything. We report the matcher we failed on, and also check generally for matchers which
    # do not match a single element
    element_defs_not_found = []
    for element_def in all_element_definitions:
        if not any(element for element in _descendant_elements(root_element) if _matches(element_def, element)):
            element_defs_not_found.append(element_def)

    return MatcherResult(spec,
                         html_src,
                         root_element,
                         passed=False,
                         element_defs_not_found=element_defs_not_found,
                         failed_on_def=current_element_def)


def _flatten_element_definitions(spec):
    """ Flattens the spec from a tree to a list using a depth first search. """

    all_element_definitions = []
    _flatten_element_definitions_rec(spec, all_element_definitions)
    return all_element_definitions


def _flatten_element_definitions_rec(current_element_def, all_element_definitions):
    all_element_definitions.append(current_element_def)
    for child in current_element_def.children:
        _flatten_element_definitions_rec(child, all_element_definitions)


def prune_unmatched_elements(root_element, spec):
    return _prune_unmatched_elements(root_element, _flatten_element_definitions(spec))


def _prune_unmatched_elements(element, all_element_definitions):
    """ Removes elements in the tree which don't match any def or carry children who match any def """

    i_match_anything = any(_matches(elem_def, element) for elem_def in all_element_definitions)

    # Now I find out whether the children match anything
    children_to_extract = []
    child_matched_anything = False
    for child_element in _child_elements(element):
        if _prune_unmatched_elements(child_element, all_element_definitions):
            child_matched_anything = True
        else:
            children_to_extract.append(child_element)
    for child_element in children_to_extract:
        child_element.extract()

    # Let the client know if anything matched
    return i_match_anything or child_matched_anything


def _matches(element_def, element):
    """ Tests whether an element matches an element definition. """
    return _name_matches(element_def, element)\
        and _content_matches(element_def, element)\
        and _attributes_match(element_def, element)


def _name_matches(element_def, element):
    """ Checks for match in the element name, performing a strict match based on the name regex in the def. """

    if element_def.name_matcher.match(element.name):
        return True
    return False


def _content_matches(element_def, element):
    """ Checks for match of content (if provided), must partially match one of the text items in the element. """

    if not element_def.content:
        return True
    for string in element.strings:
        if string and element_def.content in string:
            return True
    return False


def _attributes_match(element_def, element):
    """ Checks that the attributes in the def are found in the element, partial match of values is permitted. """

    for key, value in element_def.attrs.items():
        if key not in element.attrs or value not in element.attrs[key]:
            return False
    return True


def _child_elements(element):
    """ Helper to return the children of an element which are elements themselves. """

    return (child for child in element.children if type(child) is Tag)


def _descendant_elements(element):
    """ Helper to return the descendants of an element which are elements themselves. """

    return (child for child in element.descendants if type(child) is Tag)


# def recursive_match(self, element):
#     # Gather up each element matcher in our spec
#     all_element_matchers = []
#     self._gather_matchers(self, all_element_matchers)
#
#     # Do a single pass of the element tree, extracting any elements that don't match any matcher
#     self._matches_any_matcher(element, all_element_matchers)
#     print element.prettify()
#
#     return self._matches(element)
#
#
# def _matches_any_matcher(self, element, all_element_matchers):
#     # See if I will match anything
#     i_match_anything = False
#     for matcher in all_element_matchers:
#         if matcher._name_matches(element) and matcher._content_matches(element) and matcher._attributes_match(element):
#             i_match_anything = True
#             break
#
#     # Now I find out whether the children match anything
#     children_to_extract = []
#     child_matched_anything = False
#     for child_element in [child for child in element.children if type(child) is Tag]:
#         if self._matches_any_matcher(child_element, all_element_matchers):
#             child_matched_anything = True
#         else:
#             children_to_extract.append(child_element)
#     for child_element in children_to_extract:
#         child_element.extract()
#
#     # Let the client know if anything matched
#     return i_match_anything or child_matched_anything
#
#
# def _matches(self, element, level=0):
#     print(('    '*level) + 'Testing: {0} on element {1} {2}'.format(str(self), element.name, element.attrs))
#     if self._name_matches(element)\
#             and self._content_matches(element)\
#             and self._attributes_match(element)\
#             and self._children_match(element, level):
#         return True
#     return self._search_children_for_match(element, level)
#
#
# def _children_match(self, element, level):
#     level += 1
#
#     if not self.children:
#         return True
#
#     element_children = [child for child in element.children if type(child) is Tag]
#     child_index = 0
#     for element_child in element_children:
#         if self.children[child_index]._matches(element_child, level):
#             child_index += 1
#         if child_index == len(self.children):
#             print ('    '*level) + 'All children found!'
#             return True
#     return False
#
# def _search_children_for_match(self, element, level):
#     element_children = [child for child in element.children if type(child) is Tag]
#     for element_child in element_children:
#         if self._matches(element_child, level):
#             return True
#     return False