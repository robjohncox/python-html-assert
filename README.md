python-html-assert
==================

Utility for asserting the structure and content of HTML in python.

*Important Note:* This is very much in alpha, there will be bugs for now.

### Installation

```
pip install git+git://github.com/robjohncox/python-html-assert.git
```

### Philosophy

Test that assert HTML are often fragile, with minor changes breaking tests.
Furthermore, they are often difficult to maintain because they require
non-trivial x-path style queries to navigate through the HTML. More often than
not, the changes that break tests are caused by changes you don't even care
about from the perspective of your test assertions.

Therefore, the goal of this utility is to provide a way to assert just the
parts of an HTML document that you care about, in a way that helps make your
test less fragile. The basis of this is the specification (from here onwards
spec) which describes what you want to assert. This is a tree structure that
mimics HTML, where you only include the pieces of the document you want to
assert. This is then matched against the HTML document to verify that the items
you specify appear in the HTML, and that they follow the structure you specify,
whilst ignoring all the other parts of the HTML that you do not care about.

### Example

Lets say we have the following HTML document (either static, or generated from
a web framework like Django):

```html
<html>
  <head>
    <title>My Document</title>
  </head>
  <body>
    <h1>My Document</h1>
    <div class="main-content">
      <p>This is some text.</p>
      <table id="important-table">
        <tr><td>A</td><td>One</td></tr>
        <tr><td>B</td><td>Two</td></tr>
      </table>
    </div>
  </body>
</html>
```

We assert the items that we care about:

```python
def test_my_html(self):
    html_src = "..."

    spec = html(
        heading('My Document'),
        div(
            text('This is some text.'),
            elem('table', id='important-table)))

    self.assertTrue(html_match(spec, html_src))
```

Now, even if there are changes to the HTML that we don't care about, our test
may not break. For example, lets say that the following happens:

- New attributes are added to some elements.
- Elements we care about get nested inside additional div elements.
- A change in the underlying test data adds more rows to the table.

Even though these impact the structure of the document, when we match the spec
to the document it will be reported as OK, because the items that we care about
still appear correctly and in the right place. However, if changes happen to
the HTML document such that:

- The content of the paragraph or the heading changes.
- The table gets moved out of the main content div.
- The HTML element wrapping the document goes missing.

Then the assertion will fail.

### Running the Test Suite

The test suite can be run with the following command, in an environment where
the requirements have been installed.

```bash
py.test
```

### Further Thoughts

Some additional notes that may be of interest:

- This works very well when running tests with Selenium, as you can take the
  page source that gets loaded from the web driver.
- This is not intended to solve the world's HTML assertion problems, it will
  prove useful in some contexts, but in others this style of assertion will
  prove to be too weak and you should therefore use a different tool.
- As we develop the framework further and understand its strengths and
  limitations, we will strive to make these very clear so people can make
  conscious choices on whether this approach makes sense for them or not.

### In the Pipeline

The important enhancements we will focus on first are:

- Better error reporting, this is the single major weakness of the current
  implementation, debugging test failures can be a real pain.
- Finish an improved matcher algorithm that deals better with repeated
  elements.
- Write assertion methods using this logic for simpler integration into test
  cases.

The `todo.txt` file contains a more detailed list of upcoming tasks.
