# -*- coding: utf-8 -*-

"""
Module providing a file writer
"""
from __future__ import print_function, unicode_literals
import itertools
import re
import sys
from datetime import datetime
from io import StringIO
from os import path, environ
from platform import system
from subprocess import check_output, CalledProcessError
from cpywrite.spdx.license import License

__all__ = ['Generator', 'extensions']


class Generator(object):
    """A source file generator"""
    def __init__(self, filename='new.py', rights='GPL-3.0-or-later'):
        lang, ext, tokens = _get_language_meta(filename)

        if not lang:
            raise ValueError("Unrecognized source file extension: '%s'"
                             % (ext))

        self.rights = License(rights)
        self.out_file = path.splitext(filename)[0] + ext
        self.lang = lang
        self.tokens = tokens

    def set_file_props(self, filename, rights=''):
        """
        Update this Generator's output file, along with all associated
        properties
        """
        lang, ext, new_tokens = _get_language_meta(filename)

        if not lang:
            raise ValueError("Unrecognized source file extension: '%s'"
                             % (ext))

        if rights:
            self.rights = License(rights)
        self.out_file = path.splitext(filename)[0] + ext
        self.lang = lang
        self.tokens = new_tokens

    def fetch_license_header(self, use_license_body=False):
        """Return a license header, with or without standard language"""
        def _continue_block_comment(dest):
            try:
                tkn = self.tokens[2]
                print(tkn.rstrip() if len(tkn) < 2 else tkn, file=dest)
            except IndexError:
                print(self.tokens[0], file=dest)

        def _close_block_comment(dest):
            try:
                print(self.tokens[3], file=dest)
            except IndexError:
                print(self.tokens[0], file=dest)
            if self.lang_key == 'php':
                print('\n?>', file=dest)

        def _apply_format(text, pattern, copying, email):
            """
            Wrap text if the raw header has no break after author's email, as
            some license formats require, e.g the ECL, all of the GFDLs. Fix up
            copyright format and insert punctuation
            """
            year = str(datetime.now())[:4]
            text = re.sub(r'\)%s' % year,
                          ') ' + year,
                          re.sub(r'(?!$)<%s> ' % email,
                                 '<%s>. ' % email,
                                 pattern.sub(copying[14:], text)))

            if self.rights.spdx_code.startswith('ECL'):
                run_on_text = re.search(r'(%s).+\<(%s)\>\w' % (self.tokens[1],
                                                               email),
                                        text)
                if run_on_text:
                    text = re.sub(r'[\*\-\"#\/]*(%s)' % run_on_text.group(),
                                  '%s%s\n%s%s' % (self.tokens[1].lstrip(),
                                                  copying + \
                                                  ". Licensed under the",
                                                  self.tokens[1],
                                                  run_on_text.group()[-1]),
                                  text)
            return text

        try:
            out = StringIO()
            year = str(datetime.now())[:4]
            author, email = _get_source_author()
            copying = \
                'Copyright (c) ' + year + ' ' + author + ' <' + email + '>'
            terms = \
                self.rights.header \
                if not use_license_body \
                else self.rights.license_text
            author_date = \
                re.compile(r"(?!.*(http).*)[\<\[\s][yearxYEARX]+[\>\]\s].+[\>\]]") \
                if not self.rights.spdx_code.startswith('GFDL') \
                else re.compile(r"[\<\[\s][yearxYEARX]+[\>\]\s].+[\>\]\.]")

            if self.lang_key in _SCRIPT_HEADERS:
                print(_SCRIPT_HEADERS[self.lang_key], file=out)

            print(self.tokens[0], file=out)
            print(self.tokens[1] + path.basename(self.out_file), file=out)

            if use_license_body:
                _continue_block_comment(out)

            if terms:  # found a standard header
                def _clean_tokens(tkn, line):
                    return tkn.rstrip() if not line.strip() else tkn

                terms = \
                    '\n'.join([_clean_tokens(self.tokens[1], ln) + ln.rstrip() \
                               for ln in terms])

                if author_date.search(terms):
                    terms = _apply_format(terms, author_date, copying, email)
                else:
                    _continue_block_comment(out)
                    print(self.tokens[1] + copying, file=out)

                print(terms, file=out)

            else:  # no standard header
                _continue_block_comment(out)
                print(self.tokens[1] + copying, file=out)

                # License should return the name of any recognized license,
                # even if there's no header; just be sure to call __str__
                # explicitly
                if str(self.rights):
                    _continue_block_comment(out)
                    print(self.tokens[1] +
                          "Licensed under the terms of %s" % (self.rights),
                          file=out)

            _close_block_comment(out)

            return out.getvalue()

        except (AttributeError, IndexError, IOError, KeyError, ValueError) \
                as exc:
            print(str(exc))
        finally:
            out.close()

    @property
    def lang_key(self):
        """
        Return the normalized name of this Generator's language to aid key
        lookup
        """
        return self.lang.lower()

    def __repr__(self):
        """Return a debug string representation of this Generator"""
        return str((self.__class__.__name__, self.lang))


def _get_language_meta(filename):
    """Identify programming language from file extension"""
    if len(filename.strip()) < 1 or \
        re.match(r'^.*[`<>:\"\'\|\?\*].*$', filename) or \
            re.match(r'^.+[\-`<>:\"\'\|\?\*\.]+$', filename):
        raise ValueError("Invalid filename: '%s'" % filename)

    fname, ext = path.splitext(filename)

    if not ext or ext == '.':
        print('No extension; assuming shell script')
        return ('Bash', '', ('#', '# '))

    if ext.lower() == '.txt' and path.basename(fname).lower() == 'cmakelists':
        return ('CMake', '.txt', ('#', '# '))

    lang = ''
    tokens = ()
    ext = ext.lower()

    for k in _SOURCE_META:
        if ext in list(k):
            try:
                for grp in _SOURCE_META[k][0]:
                    if ext in list(grp) or ext == grp:
                        lang = _SOURCE_META[k][0][grp]
                        tokens = _SOURCE_META[k][1]
                        break

            except (KeyError, IndexError):
                pass

    return (lang, ext, tokens)

def _get_source_author():
    """
    Retrieve author details from local git configuration
    """
    author = \
        environ.get('USERNAME', 'unknown') \
        if system() == 'Windows' \
        else environ.get('USER', 'unknown')
    email = 'domain.org'

    try:
        author = check_output(['git',
                               'config',
                               '--get',
                               'user.name']).decode('utf-8').rstrip()

    except (IOError, OSError, CalledProcessError, AttributeError):
        pass

    try:
        email = check_output(['git',
                              'config',
                              '--get',
                              'user.email']).decode('utf-8').rstrip()

    except (IOError, OSError, CalledProcessError, AttributeError):
        try:
            email = author + '@' + \
                    check_output(['hostname']
                                 if system() == 'Windows'
                                 else ['uname', '-n']
                                ).decode('utf-8').rstrip()

        except (IOError, OSError, CalledProcessError, AttributeError):
            pass

    return (author, email)

def extensions():
    """Return a list of file extensions recognized by the Generator type"""
    return sorted('*' + e for e in \
                  filter(len,
                         set(itertools.chain(
                             (l.lower() for l in _SOURCE_META
                              if not isinstance(l, str) for l in l),
                             (lang.lower() for lang in _SOURCE_META
                              if isinstance(lang, str))))))


_SOURCE_META = {
    ('', '.sh', '.pl', '.py', '.pyw', '.rb', '.cmake'):
        [{
            ('', '.sh'): 'Bash',
            ('.pl'): 'Perl',
            ('.py', '.pyw'): 'Python',
            ('.rb'): 'Ruby',
            ('.cmake'): 'CMake'
        },
         ('#', '# ')],
    ('.lisp', '.lsp', '.cl', '.scm', '.ss', '.clj', '.cljc', '.cljs'):
        [{
            ('.lisp', '.lsp'): 'Lisp',
            ('.cl'): 'Common Lisp',
            ('.scm', '.ss'): 'Scheme',
            ('.clj', '.cljc'): 'Clojure',
            ('.cljs'): 'ClojureScript',
        },
         (';;', ';; ')],
    ('.c', '.cc', '.c++', '.cpp', '.cxx', '.cs', '.css', '.h', '.hh', '.h++',
     '.hpp', '.hxx', '.java', '.js', '.php', '.php4', '.php5', '.phtml', '.rs',
     '.ts'):
        [{
            ('.c'): 'C',
            ('.h'): 'C header',
            ('.cc', '.c++', '.cpp', '.cxx'): 'C++',
            ('.hh', '.h++', '.hpp', '.hxx'): 'C++ header',
            ('.cs'): 'C-sharp',
            ('.css'): 'CSS',
            ('.java'): 'Java',
            ('.php', '.php4', '.php5', '.phtml'): 'PHP',
            ('.js'): 'JavaScript',
            ('.ts'): 'TypeScript'
        },
         ('/**', ' * ', ' *', ' */')],
    ('.ml', '.mli'):
        [{
            ('.ml', '.mli'): 'OCaml'
        },
         ('(*', ' ', ' ', '*)')],
    ('.html', '.htm'):
        [{('.html', '.htm'): 'HTML'}, ('<!--', ' ', ' ', '-->')],
    ('.sql', '.hs', '.lhs'):
        [{
            ('.sql'): 'SQL',
            ('.hs', '.lhs'): 'Haskell',
        },
         ('--', '-- ')],
    ('.go', '.rs', '.fs', '.fsi', '.fsx', '.fsscript', '.scss'):
        [{
            ('.go'): 'Go',
            ('.rs'): 'Rust',
            ('.fs', '.fsi', '.fsx', '.fsscript'): 'F-sharp',
            ('.scss'): 'SASS'
        },
         ('//', '// ')],
    ('.vim', '.vimrc'):
        [{
            ('.vim', '.vimrc'): 'VimL'
        },
         ('""', '"" ')]
}
"""
Mapping of file extensions to comment markers for all programming languages
recognized by the Generator type
"""

_SCRIPT_HEADERS = {
    'bash': '#!/usr/bin/env bash',
    'perl': '#!/usr/bin/env perl',
    'php': '<?php',
    'python': '#!/usr/bin/env python%s\n# -*- coding: utf-8 -*-\n'
              % sys.version_info[0],
    'ruby': '# frozen_string_literal: true\n',
}
"""
Header lines for the most common scripting languages
"""
