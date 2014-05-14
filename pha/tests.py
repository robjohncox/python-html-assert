import unittest

from pha import elem, html_match, html, heading, text, a, accordion, acc_group, acc_body, acc_heading, div, input,\
    img, select, option


class BaseElementDefTests(unittest.TestCase):

    def assert_match(self, html_src, spec):
        result = html_match(spec, html_src)
        print(unicode(result))
        self.assertTrue(result.passed)

    def assert_not_match(self, html_src, spec):
        result = html_match(spec, html_src)
        print(unicode(result))
        self.assertTrue(result.failed)


class ElementDefConstructionTests(BaseElementDefTests):

    def test_element_def_construction(self):
        child_element_def = text('child')
        parent_element_def = elem('parent', child_element_def, id="abc", title="the parent")

        self.assertEquals(r'^parent$', parent_element_def.name_regex)
        self.assertIsNotNone(parent_element_def.name_matcher)
        self.assertIsNone(parent_element_def.content)
        self.assertIsNone(parent_element_def.parent)
        self.assertEquals(1, len(parent_element_def.children))
        self.assertIn(child_element_def, parent_element_def.children)
        self.assertEquals(2, len(parent_element_def.attrs))
        self.assertEquals('abc', parent_element_def.attrs['id'])
        self.assertEquals('the parent', parent_element_def.attrs['title'])

        self.assertEquals(parent_element_def, child_element_def.parent)
        self.assertEquals('child', child_element_def.content)

    def test_element_def_construction_with_content_as_keyword(self):
        element_def = elem('element', content='Some content')

        self.assertEquals('Some content', element_def.content)
        self.assertFalse('content' in element_def.attrs)

    def test_element_def_construction_with_escaped_attribute_name(self):
        element_def = elem('element', class_='some-class')

        self.assertEquals('some-class', element_def.attrs['class'])
        self.assertFalse('class_' in element_def.attrs)


class SimpleMatchingTests(BaseElementDefTests):

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


class MatchingResultTests(BaseElementDefTests):

    def test_result_object_passing(self):
        html_src = """
                    <html>
                        <p>Content found</p>
                    </html>
                   """

        spec = html(text('Content found'))

        result = html_match(spec, html_src)

        self.assertEquals(spec, result.spec)
        self.assertEquals(html_src, result.html_src)
        self.assertIsNotNone(result.root_element)
        self.assertTrue(result.passed)
        self.assertFalse(result.failed)
        self.assertEquals(0, len(result.element_defs_not_found))
        self.assertIsNone(result.failed_on_def)

    def test_result_object_failed_with_element_def_not_matching_any_element(self):
        html_src = """
                    <html>
                        <p>Content found</p>
                    </html>
                   """

        heading_not_found_def = text('Heading not found')
        text_not_found_def = text('Text not found')
        spec = html(
            heading_not_found_def,
            text('Content found'),
            text_not_found_def
        )

        result = html_match(spec, html_src)

        self.assertEquals(spec, result.spec)
        self.assertEquals(html_src, result.html_src)
        self.assertIsNotNone(result.root_element)
        self.assertFalse(result.passed)
        self.assertTrue(result.failed)
        self.assertEquals(2, len(result.element_defs_not_found))
        self.assertIn(heading_not_found_def, result.element_defs_not_found)
        self.assertIn(text_not_found_def, result.element_defs_not_found)
        self.assertEquals(heading_not_found_def, result.failed_on_def)

    def test_result_object_failed_with_matcher_not_matched_because_html_out_of_order(self):
        html_src = """
                    <html>
                        <p>Content found</p>
                        <h1>Heading not found</h1>
                    </html>
                   """

        heading_not_found_def = text('Heading not found')
        spec = html(
            heading_not_found_def,
            text('Content found'),
        )

        result = html_match(spec, html_src)

        self.assertEquals(spec, result.spec)
        self.assertEquals(html_src, result.html_src)
        self.assertIsNotNone(result.root_element)
        self.assertFalse(result.passed)
        self.assertTrue(result.failed)
        self.assertEquals(0, len(result.element_defs_not_found))
        self.assertEquals(heading_not_found_def, result.failed_on_def)


class ElementDefHelperTests(BaseElementDefTests):

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
                                        <p>Remove Me</p>
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

    def test_input_element(self):
        self.assert_match('<input id="abc" value="rob"/>', input('abc', 'rob'))
        self.assert_match('<input id="abc"/>', input('abc'))

    def test_select_element(self):
        html_src = """
                    <html>
                        <select id='abc'>
                            <option value='1'>1</option>
                            <option value='2' selected='selected'>2</option>
                            <option value='3'>3</option>
                        </select>
                    </html>
                   """

        spec = html(
            select('abc',
                   option('1', '1'),
                   option('2', '2', selected=True),
                   option('3')
            )
        )

        self.assert_match(html_src, spec)

    def test_img_element(self):
        self.assert_match('<img src="/some/file"/>', img('/some/file'))


class NestedElementDefTests(BaseElementDefTests):

    def test_content_mixed_with_tags(self):
        html_src = """
                    <a class="btn btn-small btn-primary pull-right" href="/accounts/users/new/">
                        <i class="icon-plus icon-white">
                        </i>
                        Create New User
                    </a>
                   """

        spec = a(href='/accounts/users/new/', link_text='Create New User')

        self.assert_match(html_src, spec)

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

    def test_more_complex_nested_structure(self):
        html_src = """
                    <div class="accordion-heading">
                        <div class="accordion-toggle">
                            <div class="ordericons"/>
                            <a>
                                <div>Rick</div>
                                <div>Labminds</div>
                            </a>
                        </div>
                    </div>
                   """

        spec = acc_heading(
            text('Rick'),
            text('Labminds')
        )

        self.assert_match(html_src, spec)


class ComplexElementDefTests(BaseElementDefTests):

    def test_big_example(self):
        html_src = """
                    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
                    <html xmlns="http://www.w3.org/1999/xhtml">
                     <head>
                      <title>
                       Users - LabOS
                      </title>
                     </head>
                     <body>
                      <div id="wrap">
                       <div class="navbar-wrapper">
                        <div class="navbar navbar-inverse navbar-static-top">
                         <div class="navbar-inner">
                          <div class="container">
                           <!-- Navigation menus -->
                           <div class="nav-collapse collapse">
                            <ul class="nav">
                             <!-- Admin menu -->
                             <li class="dropdown active" id="admin-dropdown">
                              <a class="dropdown-toggle" data-toggle="dropdown" href="#">
                               Admin
                               <b class="caret">
                               </b>
                              </a>
                              <ul class="dropdown-menu">
                               <li class="nav-header">
                                Manage Users
                               </li>
                               <li>
                                <a href="/accounts/users/">
                                 User List
                                </a>
                               </li>
                               <li>
                                <a href="/accounts/users/new/">
                                 Create New User
                                </a>
                               </li>
                              </ul>
                             </li>
                            </ul>
                            <!-- User menu -->
                            <ul class="nav pull-right">
                             <li class="dropdown" id="user-dropdown">
                              <a class="dropdown-toggle" data-toggle="dropdown" href="#">
                               <i class="icon-user icon-white">
                               </i>
                               <strong>
                                Ricklef
                               </strong>
                               (Labminds)
                               <b class="caret">
                               </b>
                              </a>
                              <ul class="dropdown-menu">
                               <li>
                                <a href="/accounts/users/Ricklef/profile/">
                                 View Profile
                                </a>
                               </li>
                               <li>
                                <a href="/auth/change-password/?next=/accounts/users/">
                                 Change Password
                                </a>
                               </li>
                               <li class="divider">
                               </li>
                               <li>
                                <a href="/accounts/users/feedback">
                                 Feedback
                                </a>
                               </li>
                               <li class="divider">
                               </li>
                               <li>
                                <a href="/auth/logout/">
                                 Logout
                                </a>
                               </li>
                              </ul>
                             </li>
                            </ul>
                           </div>
                          </div>
                         </div>
                        </div>
                       </div>
                       <div class="container">
                        <!-- Support for displaying django user messages -->
                        <!-- Display page heading -->
                        <div class="row-fluid">
                         <span class="span12">
                          <h3>
                           Users
                          </h3>
                         </span>
                        </div>
                        <!-- Placeholder for the main content pane -->
                        <a class="btn btn-small btn-primary pull-right" href="/accounts/users/new/">
                         <i class="icon-plus icon-white">
                         </i>
                         Create New User
                        </a>
                        <h4>
                         Active Users
                        </h4>
                        <div class="accordion" id="active_users">
                         <div class="accordion-group">
                          <div class="accordion-heading row-fluid">
                           <div class="accordion-toggle group-accordion-toggle">
                            <div class="ordericons pull-right dropdown">
                             <!-- User functions -->
                             <div class="btn-group" id="btn_group_Ricklef">
                              <a class="btn btn-small btn-primary" href="/accounts/users/Ricklef/profile/">
                               <i class="icon-user icon-white">
                               </i>
                               <span class="hidden-phone">
                                View Profile
                               </span>
                              </a>
                              <button class="btn btn-small btn-primary dropdown-toggle" data-toggle="dropdown">
                               <span class="caret">
                               </span>
                              </button>
                              <ul class="dropdown-menu">
                               <li>
                                <a class="btn btn-small btn-primary" href="/accounts/users/Ricklef/profile/">
                                 <i class="icon-user">
                                 </i>
                                 View Profile
                                </a>
                               </li>
                              </ul>
                             </div>
                            </div>
                            <a data-parent="#active_users" data-toggle="collapse" href="#active_users_Ricklef_body">
                             <div class="span4">
                              <strong>
                               Ricklef Wohlers (Ricklef)
                              </strong>
                             </div>
                             <div class="span5 hidden-phone muted">
                              Labminds (admin)
                             </div>
                            </a>
                           </div>
                          </div>
                          <div class="accordion-body collapse" id="active_users_Ricklef_body">
                           <div class="accordion-inner">
                            <div class="row-fluid">
                             <div class="span8 well">
                              <table class="table table-condensed">
                               <thead>
                                <tr>
                                 <th colspan="2">
                                  User Details
                                 </th>
                                </tr>
                               </thead>
                               <tr>
                                <td>
                                 Username
                                </td>
                                <td>
                                 Ricklef
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Org Group
                                </td>
                                <td>
                                 Labminds
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Permission Group
                                </td>
                                <td>
                                 admin
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Email Address
                                </td>
                                <td>
                                 ricklef@labminds.co.uk
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Date Setup
                                </td>
                                <td>
                                 May 13, 2014, 7:35 a.m.
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Last Login
                                </td>
                                <td>
                                 May 13, 2014, 7:35 a.m.
                                </td>
                               </tr>
                              </table>
                             </div>
                             <div class="span4 well">
                              <img src="/static/img/user_icons/male_long.png" width="280"/>
                             </div>
                            </div>
                           </div>
                          </div>
                         </div>
                         <div class="accordion-group">
                          <div class="accordion-heading row-fluid">
                           <div class="accordion-toggle group-accordion-toggle">
                            <div class="ordericons pull-right dropdown">
                             <!-- User functions -->
                             <div class="btn-group" id="btn_group_Ville">
                              <a class="btn btn-small btn-primary" href="/accounts/users/Ville/profile/">
                               <i class="icon-user icon-white">
                               </i>
                               <span class="hidden-phone">
                                View Profile
                               </span>
                              </a>
                              <button class="btn btn-small btn-primary dropdown-toggle" data-toggle="dropdown">
                               <span class="caret">
                               </span>
                              </button>
                              <ul class="dropdown-menu">
                               <!-- Activate/deactivate user -->
                               <li>
                                <a href="/accounts/users/Ville/deactivate/">
                                 <i class="icon-remove">
                                 </i>
                                 Deactivate
                                </a>
                               </li>
                               <!-- Change users group -->
                               <li>
                                <a href="/accounts/users/Ville/change-group/admin">
                                 <i class="icon-hand-up">
                                 </i>
                                 Grant Admin Privileges
                                </a>
                               </li>
                              </ul>
                             </div>
                            </div>
                            <a data-parent="#active_users" data-toggle="collapse" href="#active_users_Ville_body">
                             <div class="span4">
                              <strong>
                               Ville Lehtonen (Ville)
                              </strong>
                             </div>
                             <div class="span5 hidden-phone muted">
                              Labminds (users)
                             </div>
                            </a>
                           </div>
                          </div>
                          <div class="accordion-body collapse" id="active_users_Ville_body">
                           <div class="accordion-inner">
                            <div class="row-fluid">
                             <div class="span8 well">
                              <table class="table table-condensed">
                               <thead>
                                <tr>
                                 <th colspan="2">
                                  User Details
                                 </th>
                                </tr>
                               </thead>
                               <tr>
                                <td>
                                 Username
                                </td>
                                <td>
                                 Ville
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Org Group
                                </td>
                                <td>
                                 Labminds
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Permission Group
                                </td>
                                <td>
                                 users
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Email Address
                                </td>
                                <td>
                                 ville@labminds.co.uk
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Date Setup
                                </td>
                                <td>
                                 May 13, 2014, 7:35 a.m.
                                </td>
                               </tr>
                               <tr>
                                <td>
                                 Last Login
                                </td>
                                <td>
                                 May 13, 2014, 7:35 a.m.
                                </td>
                               </tr>
                              </table>
                             </div>
                             <div class="span4 well">
                              <img src="/static/img/user_icons/male_long.png" width="280"/>
                             </div>
                            </div>
                           </div>
                          </div>
                         </div>
                        </div>
                       </div>
                      </div>
                     </body>
                    </html>
                   """

        spec = html(
            div(
                div(
                    heading('Users')
                ),
                a(href='/accounts/users/new/', link_text='Create New User'),
                heading('Active Users'),
                accordion(
                    acc_group(
                        acc_heading(
                            a(href='/accounts/users/Ricklef/profile/'),
                            text('Ricklef Wohlers (Ricklef)'),
                            text('Labminds (admin)'),
                        )
                    )
                )
            )
        )

        self.assert_match(html_src, spec)

    def test_that_fails_when_we_use_the_recursive_parser(self):
        from pha import pretty_spec

        html_src = """
                    <html xmlns="http://www.w3.org/1999/xhtml">
                     <body>
                      <div id="wrap">
                       <div class="navbar-wrapper" MATCH="2">
                        <div class="navbar navbar-inverse navbar-static-top">
                         <div class="navbar-inner">
                          <div class="container">
                           <!-- Navigation menus -->
                           <div class="nav-collapse collapse">
                           </div>
                          </div>
                         </div>
                        </div>
                       </div>
                       <div class="container">
                        <!-- Support for displaying django user messages -->
                        <!-- Display page heading -->
                        <div class="row-fluid">
                         <span class="span12">
                          <h3 MATCH="3">
                           Users
                          </h3>
                         </span>
                        </div>
                        <!-- Placeholder for the main content pane -->
                        <a class="btn btn-small btn-primary pull-right" href="/accounts/users/new/">
                         <i class="icon-plus icon-white">
                         </i>
                         Create New User
                        </a>
                        <h4>
                         Active Users
                        </h4>
                        <div class="accordion" id="active_users">
                         <div class="accordion-group">
                          <div class="accordion-heading row-fluid">
                           <div class="accordion-toggle group-accordion-toggle">
                            <div class="ordericons pull-right dropdown">
                             <!-- User functions -->
                             <div class="btn-group" id="btn_group_Ricklef">
                              <a class="btn btn-small btn-primary" href="/accounts/users/Ricklef/profile/">
                               <i class="icon-user icon-white">
                               </i>
                               <span class="hidden-phone">
                                View Profile
                               </span>
                              </a>
                              <button class="btn btn-small btn-primary dropdown-toggle" data-toggle="dropdown">
                               <span class="caret">
                               </span>
                              </button>
                              <ul class="dropdown-menu">
                               <li>
                                <a class="btn btn-small btn-primary" href="/accounts/users/Ricklef/profile/">
                                 <i class="icon-user">
                                 </i>
                                 View Profile
                                </a>
                               </li>
                              </ul>
                             </div>
                            </div>
                            <a data-parent="#active_users" data-toggle="collapse" href="#active_users_Ricklef_body">
                             <div class="span4">
                              <strong>
                               Ricklef Wohlers (Ricklef)
                              </strong>
                             </div>
                             <div class="span5 hidden-phone muted">
                              Labminds (admin)
                             </div>
                            </a>
                           </div>
                          </div>
                         </div>
                        </div>
                       </div>
                      </div>
                     </body>
                    </html>
                   """

        spec = html(
            div(
                div(heading('Users')),
                a(href='/accounts/users/new/', link_text='Create New User'),
                heading('Active Users'),
                accordion(
                    acc_group(
                        acc_heading(
                            text('Ricklef Wohlers (Ricklef)'),
                            text('Labminds (admin)'),
                        )
                    )
                )
            )
        )

        self.assert_match(html_src, spec)


if __name__ == '__main__':
    unittest.main()        
