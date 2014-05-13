import unittest

from pha import elem, html_matches, html, heading, text, a, accordion, acc_group, acc_body, acc_heading, div


class UnitTests(unittest.TestCase):

    def test_root_element_match(self):
        self.assert_match('<html></html>', elem('html'))

    def test_closed_root_element_match(self):
        self.assert_match('<html/>', elem('html'))

    def test_non_root_element_match(self):
        self.assert_match('<html><head/><body><div></div></body></html>', elem('div'))

    def test_element_not_matched(self):
        self.assert_not_match('<html></html>', elem('div'))

    def test_element_with_attribute_match(self):
        self.assert_match('<html><body id="the_body"></body></html>', elem('body', id='the_body'))

    def test_element_with_multiple_attributes_match(self):
        self.assert_match('<html><body id="the_body" title="some_name"/></html>',
                          elem('body', id='the_body', title='some_name'))

    def test_element_with_attribute_match_when_element_has_additional_attributes(self):
        self.assert_match('<html><body id="the_body" title="some_name"/></html>',
                          elem('body', id='the_body'))

    def test_element_with_one_attribute_wrong_value_not_matched(self):
        self.assert_not_match('<html><body id="the_body" title="some_name"/></html>',
                              elem('body', id='the_body', title='some_other_name'))

    def test_element_with_one_attribute_missing_not_matched(self):
        self.assert_not_match('<html><body id="the_body"></body></html>',
                              elem('body', id='the_body', title='other_name'))

    def test_element_with_one_attribute_partial_match(self):
        self.assert_match('<html><body id="this_is_the_body"></body></html>', elem('body', id='is_the'))

    def test_element_with_content_match(self):
        self.assert_match('<html><body><p>This is some content</p></body></html>',
                          elem('p', content='This is some content'))

    def test_element_with_content_partial_match(self):
        self.assert_match('<html><body><p>This is some content</p></body></html>', elem('p', content='some'))

    def test_element_with_content_not_match(self):
        self.assert_not_match('<html><body><p>This is some content</p></body></html>',
                              elem('p', content='This is some different content'))

    def test_nested_elements_match(self):
        self.assert_match('<html><body/></html>', elem('html', elem('body')))

    def test_nested_elements_with_wrong_child_element_not_matched(self):
        self.assert_not_match('<html><body/></html>', elem('html', (elem('div'))))

    def test_html_element(self):
        self.assert_match('<html/>', html())

    def test_heading_element(self):
        self.assert_match('<html><h1>Hello</h1></html>', heading('Hello'))
        self.assert_match('<html><h3>Hello</h3></html>', html(heading('Hello')))
        self.assert_not_match('<html><h1>Goodbye</h1></html>', heading('Hello'))

    def test_text_element(self):
        self.assert_match('<html><p>This is some text</p></html>', text('This is some text'))
        self.assert_not_match('<html><p>This is some other text</p></html>', text('This is some text'))

    def test_link_element(self):
        self.assert_match('<html><a href="www.google.com">Google</a></html>', a(href="www.google.com", content="Google"))
        self.assert_match('<html><a href="www.google.com">Google</a></html>', a(href="www.google.com"))
        self.assert_match('<html><a href="www.google.com">Google</a></html>', a(content="Google"))
        self.assert_match('<html><a href="www.google.com">Google</a></html>', a())

    def test_accordion(self):
        html_src = """
                    <html>
                        <body>
                            <div class="accordion">
                                <div class="accordion-group">
                                    <div class="accordion-heading">
                                        <p>Rick</p>
                                        <a href="www.rick.com">Rick Website</a>
                                    </div>
                                    <div class="accordion-body">
                                        <h1>Foo</h1>
                                    </div>
                                </div>
                                <div class="accordion-group">
                                    <div class="accordion-heading">
                                        <p>Tom</p>
                                        <a href="www.tom.com">Tom Website</a>
                                    </div>
                                    <div class="accordion-body">
                                        <h1>Bar</h1>
                                    </div>
                                </div>
                            </div>
                        </body>
                    </html>
                   """

        spec = html(
            accordion(
                acc_group(
                    acc_heading(
                        text('Rick'),
                        a(href='www.rick.com', link_text='Rick Website')
                    ),
                    acc_body(
                        heading('Foo')
                    )
                ),
                acc_group(
                    acc_heading(
                        text('Tom'),
                        a(href='www.tom.com', link_text='Tom Website')
                    ),
                    acc_body(
                        heading('Bar')
                    )
                )
            )
        )

        self.assert_match(html_src, spec)

    def test_div_element(self):
        self.assert_match('<html><div class="rob"></div></html>', html(div(class_='rob')))

    def test_nested_recursive_first_element(self):
        html_src = """
                    <html>
                        <div>
                            <h1>Hello</h1>
                        </div>
                        <p>Content</p>
                        <a href="www.google.com">Google</a>
                    </html>
                   """

        spec = html(
            heading('Hello'),
            text('Content'),
            a(href='www.google.com', link_text='Google')
        )

        self.assert_match(html_src, spec)

    def test_nested_recursive_middle_element(self):
        html_src = """
                    <html>
                        <h1>Hello</h1>
                        <div>
                            <p>Content</p>
                        </div>
                        <a href="www.google.com">Google</a>
                    </html>
                   """

        spec = html(
            heading('Hello'),
            text('Content'),
            a(href='www.google.com', link_text='Google')
        )

        self.assert_match(html_src, spec)

    def assert_match(self, html_src, spec):
        self.assertTrue(html_matches(spec, html_src))

    def assert_not_match(self, html_src, spec):
        self.assertFalse(html_matches(spec, html_src))


if __name__ == '__main__':
    unittest.main()        
