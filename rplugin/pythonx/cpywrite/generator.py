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
from cpywrite.spdx.license import License, in_pub_domain

__all__ = ['Generator', 'extensions']


class Generator(object):
    """A source file generator"""
    def __init__(self, filename='new.py', rights='GPL-3.0-or-later'):
        self.set_file_props(filename, rights)

    def set_file_props(self, filename, rights=''):
        """
        Set this Generator's output file, along with all associated properties
        """
        lang, ext, tokens = _get_language_meta(filename)

        if not lang:
            raise ValueError("Unrecognized source file extension: '%s'"
                             % (ext))

        if rights:
            self.rights = License(rights)
        self.out_file = path.splitext(filename)[0] + ext
        self.lang = lang
        self.tokens = tokens

    def fetch_license_header(self, full_text=False):
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

        def _apply_format(text, pattern, author, email, year):
            authorship = year + ' ' + author + ' <' + email + '>'

            # watch out for 20^th-century year template of the older GPLs
            text = \
                pattern.sub(authorship,
                            re.sub(r'(%s).+[19]*[xy]{2,} .*\n' % self.tokens[1],
                                   '', text, re.IGNORECASE))
            # fix up copyright format and insert punctuation
            if self.rights.spdx_code.startswith('GFDL'):
                text = re.sub(r'\)%s' % year,
                              ') ' + year,
                              re.sub(r'(%s).+(\w+Permission)' % self.tokens[1],
                                     '%sPermission' % self.tokens[1],
                                     re.sub(r'(?!$)<%s> ' % email,
                                            '<%s>. ' % email,
                                            text)))
            # wrap text if raw header has no break after author's email
            if self.rights.spdx_code.startswith('ECL'):
                run_on_text = re.search(r'(%s).+((%s)|\<(%s)\>)\w' \
                                        % (self.tokens[1], author, email),
                                        text)
                if run_on_text:
                    one_liner = \
                        'Copyright (c) ' + authorship + ' Licensed under the'
                    text = re.sub(r'[\*(%s)]*(%s)'
                                  % (self.tokens[1], run_on_text.group()),
                                  '%s%s\n%s%s'
                                  % (self.tokens[1],
                                     one_liner,
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
                if not full_text \
                else self.rights.license_text
            author_date = \
                re.compile(r"(?!.*(http).*)[\<\[\s][YEARX]+[\>\]\s].+[\>\]]",
                           re.IGNORECASE)

            if self.lang_key in _SCRIPT_HEADERS:
                print(_SCRIPT_HEADERS[self.lang_key], file=out)

            print(self.tokens[0], file=out)
            print(self.tokens[1] + path.basename(self.out_file), file=out)

            if full_text:
                _continue_block_comment(out)

            if ''.join(terms).strip():  # found a standard header
                def _clean_tokens(tkn, line):
                    return tkn.rstrip() if not line.strip() else tkn

                terms = \
                    '\n'.join([_clean_tokens(self.tokens[1], ln) + ln.rstrip() \
                               for ln in terms])

                if not author_date.search(terms) and not full_text:
                    # probably a GFDL or older GPL with an oddball authorship
                    # template
                    author_date = \
                        re.compile(r"(?!.*(http).*)[\<\[\s][YEARX]+[\>\]\s].+[\>\]\.]",
                                   re.IGNORECASE)

                terms = _apply_format(terms, author_date, author, email, year)

                if not re.findall(r'(<%s>)' % email, terms, re.MULTILINE) \
                   and not in_pub_domain(self.rights.spdx_code):
                    # no authorship template, so use our own
                    _continue_block_comment(out)
                    print(self.tokens[1] + copying, file=out)

                print(terms, file=out)

            else:  # no standard header
                if not in_pub_domain(self.rights.spdx_code):
                    _continue_block_comment(out)
                    print(self.tokens[1] + copying, file=out)

                # License should return the name of any recognized license,
                # even if there's no header; just be sure to call __str__
                # explicitly
                if str(self.rights):
                    _continue_block_comment(out)
                    print(self.tokens[1] + \
                          ('Licensed' \
                          if not in_pub_domain(self.rights.spdx_code) \
                          else 'Distributed') + \
                          " under the terms of %s" % (self.rights),
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


def extensions():
    """Return a list of file extensions recognized by the Generator type"""
    return sorted('*' + e for e in \
                  filter(len,
                         set(itertools.chain(
                             (l.lower() for l in _SOURCE_META
                              if not l[0] == '.' for l in l),
                             (lang.lower() for lang in _SOURCE_META
                              if lang[0] == '.')))))

def _get_language_meta(filename):
    """Identify programming language from file extension"""
    if len(filename.strip()) < 1 or \
        re.match(r'^.*[`<>:\"\'\|\?\*].*$', filename) or \
            re.match(r'^.+[\-`<>:\"\'\|\?\*\.]+$', filename):
        raise ValueError("Invalid filename: '%s'" % filename)

    fname, ext = path.splitext(filename)

    if not ext:
        if fname.startswith('.'):
            if path.basename(fname).lower()[1:] == 'vimrc':
                return ('Vimrc', '', ('""', '"" '))

            return ('dot', '', ('#', '# '))

        print('No extension; assuming shell script')
        return ('Shell script', '', ('#', '# '))

    if ext.lower() == '.txt' and path.basename(fname).lower() == 'cmakelists':
        return ('CMake', '.txt', ('#', '# '))

    lang = ''
    tokens = ()
    ext = ext.lower()

    for k in _SOURCE_META:
        # keys of only one element will get expanded into a char sequence
        exts = [k] if k[0] == '.' else k
        if ext in exts:
            try:
                for grp in _SOURCE_META[k][0]:
                    if ext in grp or ext == grp:
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

_SOURCE_META = {
    ('', '.cmake', '.ex', '.exs', '.pl', '.py', '.pyw', '.rb', '.sh'):
        [{
            ('.ex', '.exs'): 'Elixir',
            ('', '.sh'): 'Shell script',
            ('.pl'): 'Perl',
            ('.py', '.pyw'): 'Python',
            ('.rb'): 'Ruby',
            ('.cmake'): 'CMake'
        },
         ('#', '# ')],
    ('.coffee', '.litcoffee'):
        [{('.coffee', '.litcoffee'): 'CoffeeScript'}, ('###', ' ', ' ', '###')],
    ('.asm', '.s'):
        [{('.asm', '.s'): 'Assembly',}, (';', '; ')],
    ('.lisp', '.lsp', '.cl', '.scm', '.ss', '.clj', '.cljc', '.cljs'):
        [{
            ('.lisp', '.lsp'): 'Lisp',
            ('.cl'): 'Common Lisp',
            ('.scm', '.ss'): 'Scheme',
            ('.clj', '.cljc'): 'Clojure',
            ('.cljs'): 'ClojureScript',
        },
         (';;', ';; ')],
    ('.erl', '.hrl'):
        [{
            ('.erl'): 'Erlang',
            ('.hrl'): 'Erlang header'
        },
         ('%%', '%% ')],
    ('.pas', '.pp', '.inc'):
        [{('.pas', '.pp', '.inc'): 'Pascal'}, ('{', ' ', ' ', '}')],
    ('.c', '.cc', '.c++', '.cpp', '.cxx', '.cs', '.css', '.h', '.hh', '.h++',
     '.hpp', '.hxx', '.java', '.js', '.kt', '.kts', '.ktm', '.m', '.mm',
     '.php', '.php4', '.php5', '.phtml', '.ts'):
        [{
            ('.c'): 'C',
            ('.h'): 'C header',
            ('.cc', '.c++', '.cpp', '.cxx'): 'C++',
            ('.hh', '.h++', '.hpp', '.hxx'): 'C++ header',
            ('.cs'): 'C-sharp',
            ('.css'): 'CSS',
            ('.java'): 'Java',
            ('.kt', '.kts', '.ktm'): 'Kotlin',
            ('.m', '.mm'): 'Objective-C',
            ('.php', '.php4', '.php5', '.phtml'): 'PHP',
            ('.js'): 'JavaScript',
            ('.ts'): 'TypeScript'
        },
         ('/**', ' * ', ' *', ' */')],
    ('.elm'):
        [{('.elm'): 'Elm'}, ('{-', ' ', ' ', '-}')],
    ('.ml', '.mli'):
        [{('.ml', '.mli'): 'OCaml'}, ('(*', ' ', ' ', '*)')],
    ('.html', '.htm'):
        [{('.html', '.htm'): 'HTML'}, ('<!--', ' ', ' ', '-->')],
    ('.adb', '.ads', '.lua', '.sql', '.hs', '.lhs'):
        [{
            ('.adb', '.ads'): 'Ada',
            ('.lua'): 'Lua',
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
    ('.vim'): [{('.vim'): 'VimL'}, ('""', '"" ')]
}
"""
Mapping of file extensions to comment markers for all programming languages
recognized by the Generator type
"""

_SCRIPT_HEADERS = {
    'shell script': '#!/usr/bin/env bash',
    'perl': '#!/usr/bin/env perl',
    'php': '<?php',
    'python': '#!/usr/bin/env python%s\n# -*- coding: utf-8 -*-\n'
              % sys.version_info[0],
    'ruby': '# frozen_string_literal: true\n',
}
"""
Header lines for the most common scripting languages
"""
