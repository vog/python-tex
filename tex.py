"""Convert LaTeX or TeX source to PDF or DVI, and escape strings for LaTeX.

:Version:   0.1
:Requires:  Python 2.4 or higher
:Author:    Volker Grabsch <vog@notjusthosting.com>
:License:
    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject
    to the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import string
import random
import os
import os.path
import tempfile
import subprocess

def _file_read(filename):
    """Read the contents of a file and close it properly."""
    f = file(filename, 'rb')
    contents = f.read()
    f.close()
    return contents

def _file_write(filename, contents):
    """Write into a file and close it properly."""
    f = file(filename, 'wb')
    f.write(contents)
    f.close()

def convert(tex_source, input_format, output_format, max_runs=5):
    """Convert LaTeX or TeX source to PDF or DVI."""
    # check and convert arguments
    if isinstance(tex_source, unicode):
        tex_source = tex_source.encode('UTF-8')
    try:
        (tex_cmd, output_suffix) = {
            ('tex',   'dvi'): ('tex',      '.dvi'),
            ('latex', 'dvi'): ('latex',    '.dvi'),
            ('tex',   'pdf'): ('pdftex',   '.pdf'),
            ('latex', 'pdf'): ('pdflatex', '.pdf'),
            }[(input_format, output_format)]
    except KeyError:
        raise ValueError('Unable to handle conversion: %s -> %s'
                         % (input_format, output_format))
    if max_runs < 2:
        raise ValueError('max_runs must be at least 2.')
    # create temporary directory
    tex_dir = tempfile.mkdtemp(suffix='', prefix='tex-temp-')
    try:
        # create LaTeX source file
        tex_filename = os.path.join(tex_dir, 'texput.tex')
        _file_write(tex_filename, tex_source)
        # run LaTeX processor as often as necessary
        aux_old = None
        for i in xrange(max_runs):
            tex_process = subprocess.Popen(
                [tex_cmd,
                    '-interaction=batchmode',
                    '-halt-on-error',
                    '-no-shell-escape',
                    tex_filename,
                ],
                stdin=file(os.devnull, 'r'),
                stdout=file(os.devnull, 'w'),
                stderr=subprocess.STDOUT,
                close_fds=True,
                shell=False,
                cwd=tex_dir,
                env={},
            )
            tex_process.wait()
            if tex_process.returncode != 0:
                log = _file_read(os.path.join(tex_dir, 'texput.log'))
                raise ValueError(log)
            aux = _file_read(os.path.join(tex_dir, 'texput.aux'))
            if aux == aux_old:
                # aux file stabilized
                try:
                    return _file_read(os.path.join(tex_dir, 'texput' + output_suffix))
                except:
                    raise ValueError('No output file was produced.')
            aux_old = aux
        raise ValueError("%s didn't stabilize after %i runs"
                         % ('texput.aux', max_runs))
    finally:
        # remove temporary directory
        for filename in os.listdir(tex_dir):
            os.remove(os.path.join(tex_dir, filename))
        os.rmdir(tex_dir)

def tex2dvi(tex_source, **kwargs):
    """Convert TeX source to DVI."""
    return convert(tex_source, 'tex', 'dvi', **kwargs)

def latex2dvi(tex_source, **kwargs):
    """Convert LaTeX source to DVI."""
    return convert(tex_source, 'latex', 'dvi', **kwargs)

def tex2pdf(tex_source, **kwargs):
    """Convert TeX source to PDF."""
    return convert(tex_source, 'tex', 'pdf', **kwargs)

def latex2pdf(tex_source, **kwargs):
    """Convert LaTeX source to PDF."""
    return convert(tex_source, 'latex', 'pdf', **kwargs)

_latex_special_chars = {
    u"$":  u"\\$",
    u"%":  u"\\%",
    u"&":  u"\\&",
    u"#":  u"\\#",
    u"_":  u"\\_",
    u"{":  u"\\{",
    u"}":  u"\\}",
    u"[":  u"{[}",
    u"]":  u"{]}",
    u'"':  u"{''}",
    u"\\": u"\\textbackslash{}",
    u"~":  u"\\textasciitilde{}",
    u"<":  u"\\textless{}",
    u">":  u"\\textgreater{}",
    u"^":  u"\\textasciicircum{}",
    u"`":  u"{}`",   # avoid ?` and !`
    u"\n": u"\\\\",
}

def escape_latex(s):
    r"""Escape a unicode string for LaTeX.

    :Warning:
        The source string must not contain empty lines such as:
            - u"\n..." -- empty first line
            - u"...\n\n..." -- empty line in between
            - u"...\n" -- empty last line

    :Parameters:
        - `s`: unicode object to escape for LaTeX

    >>> s = u'\\"{}_&%a$b#\nc[]"~<>^`\\'
    >>> escape_latex(s)
    u"\\textbackslash{}{''}\\{\\}\\_\\&\\%a\\$b\\#\\\\c{[}{]}{''}\\textasciitilde{}\\textless{}\\textgreater{}\\textasciicircum{}{}`\\textbackslash{}"
    >>> print s
    \"{}_&%a$b#
    c[]"~<>^`\
    >>> print escape_latex(s)
    \textbackslash{}{''}\{\}\_\&\%a\$b\#\\c{[}{]}{''}\textasciitilde{}\textless{}\textgreater{}\textasciicircum{}{}`\textbackslash{}
    """
    return u''.join(_latex_special_chars.get(c, c) for c in s)

def _test():
    """Run all doc tests of this module."""
    import doctest, tex
    return doctest.testmod(tex)

if __name__ == "__main__":
    _test()
