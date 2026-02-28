# -*- coding: utf-8 -*-

"""
Module providing a file writer
"""
import re
import sys
from datetime import datetime
from io import StringIO
from itertools import chain
from os import path, environ
from platform import system
from subprocess import check_output, CalledProcessError
from cpywrite.spdx.license import License, in_pub_domain

__all__ = ['Generator', 'extensions']


class Generator():
    """A source file generator"""
    def __init__(self, filename='new.py', vim_filetype='python', rights='Apache-2.0'):
        self.set_file_props(filename, vim_filetype, rights)

    def set_file_props(self, filename, filetype='', rights=''):
        """
        Set this Generator's output file, along with all associated properties
        """
        lang, ext, tokens = _get_language_meta(filename, filetype)

        if not lang:
            raise ValueError("Unrecognized source file extension: '%s'"
                             % (ext))

        if rights:
            self.rights = License(rights)
        self.out_file = path.splitext(filename)[0] + ext
        self.lang = lang
        self.tokens = tokens

    def fetch_license_header(self, full_text=False, cpu_readable=False,
                             no_name=False, no_anon=False):
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
            authorship = year + ' ' + author

            # watch out for 20^th-century year template of the older GPLs
            text = \
                pattern.sub(authorship,
                            re.sub(r'(%s).+[19]*[xy]{2,} .*\n' % self.tokens[1],
                                   '', text, flags=re.IGNORECASE))
            # fix up copyright format and insert punctuation
            if self.rights.spdx_code.startswith('GFDL'):
                text = re.sub(r'\)%s' % year,
                              ') ' + year,
                              re.sub(r'(%s).+(\w+Permission)' % self.tokens[1],
                                     '%sPermission' % self.tokens[1], text))
            # wrap text if raw header has no break after author's email
            elif self.rights.spdx_code.startswith('ECL'):
                run_on_text = re.search(r'(%s).+((%s)|(%s))\w' \
                                        % (self.tokens[1],
                                           author,
                                           re.escape(email)),
                                        text)

                if run_on_text:
                    one_liner = \
                        'Copyright (c) ' + authorship + '. Licensed under the'
                    text = re.sub(r'[\*(%s)]*(%s)'
                                  % (self.tokens[1],
                                     re.escape(run_on_text.group())),
                                  '%s%s\n%s%s'
                                  % (self.tokens[1],
                                     one_liner,
                                     self.tokens[1],
                                     run_on_text.group()[-1]),
                                  text)
                else:
                    text = re.sub(r'(%s)' % re.escape(authorship),
                                  authorship + email,
                                  text)
            else:
                text = re.sub(r'(%s)' % re.escape(authorship),
                              authorship + email,
                              text)

            return text

        try:
            out = StringIO()
            year = str(datetime.now())[:4]
            author, contact = _get_source_author()
            # use the tag prefix specified by REUSE
            # https://reuse.software/spec/#comment-headers
            copying = \
                'Copyright (c) ' \
                if not cpu_readable \
                else 'SPDX-FileCopyrightText: '
            copying += year + ' ' + author + contact
            copyrightable = \
                no_anon or cpu_readable or \
                not in_pub_domain(self.rights.spdx_code)

            if full_text and not cpu_readable:
                terms = self.rights.license_text
            elif cpu_readable:
                terms = [self.rights.tag]
            else:
                terms = self.rights.header

            # Replace historical copyrights only when deemed optional by the SPDX,
            # e.g. https://spdx.org/licenses/0BSD.html
            # This prevents faulty matches with the FSF ZIP code in the GPL v1 and 2
            author_date_re = \
                r'(?!.*(http).*)(\.{3,}|[\<\(\[\s%s]((YEAR)%s|[YX]+)[\>\)\]\s,-].+[\>\)\]\w+])' \
                % ((r'\d', r'|\d{3}') \
                   if self.rights.spdx_code == '0BSD' \
                   else ('', '')) \
                if not (self.rights.spdx_code.startswith('ECL') or \
                        self.rights.spdx_code.startswith('GFDL')) and \
                   not self.rights.spdx_code in ['Apache-2.0', 'GD', 'X11'] \
                else r'(?!.*(http).*)[\<\[\s]((YEAR)|[YX]+)[\>\]\s].+[\>\]]'
            author_date = re.compile(author_date_re, re.IGNORECASE)

            if self.lang_key in _SCRIPT_HEADERS:
                print(_SCRIPT_HEADERS[self.lang_key], file=out)
            elif self.tokens[0].startswith('"'):
                terms = [ln.replace('"', '\'') for ln in terms]

            print(self.tokens[0], file=out)

            if not no_name:
                print(self.tokens[1] + path.basename(self.out_file), file=out)
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
                        re.compile(r"(?!.*(http).*)[\<\[\s]((YEAR)|[YX]+)[\>\]\s].+[\>\]\.]",
                                   re.IGNORECASE)

                terms = _apply_format(terms, author_date, author, contact, year)

                if not re.findall(r'(%s)' % author,
                                  terms,
                                  re.MULTILINE) \
                   and copyrightable:
                    # no authorship template, so use our own
                    print(self.tokens[1] + copying, file=out)
                    _continue_block_comment(out)

                print(terms, file=out)

            else:  # no standard header
                if copyrightable:
                    print(self.tokens[1] + copying, file=out)

                # License should return the name of any recognized license,
                # even if there's no header; just be sure to call __str__
                # explicitly
                if str(self.rights):
                    if copyrightable:
                        _continue_block_comment(out)
                    print(self.tokens[1] + str(self.rights), file=out)

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
                         set(chain(
                             (l.lower() for l in _SOURCE_META
                              if not l[0] == '.' for l in l),
                             (lang.lower() for lang in _SOURCE_META
                              if lang[0] == '.')))))

def _get_language_meta(filename, filetype=''):
    """Identify programming language from file extension or Vim file type"""
    if not bool(filename.strip()) or \
        re.match(r'^.*[`<>:\"\'\|\?\*].*$', filename) or \
            re.match(r'^.+[\-`<>:\"\'\|\?\*\.]+$', filename):
        raise ValueError("Invalid filename: '%s'" % filename)

    fname, ext = path.splitext(filename)

    if fname.startswith('.'):
        if 'vim' in fname.lower() or fname.lower().endswith('exrc'):
            return ('VimL', '', ('""', '"" '))

        if filetype == 'xdefaults':
            return (filetype.capitalize(), '', ('!', '! '))

        if not filetype:
            return ('dot', '', ('#', '# '))

    if path.basename(fname).lower() in ['dockerfile', 'make', 'makefile', 'gnumakefile']:
        return (path.basename(fname).capitalize(), '', ('#', '# '))

    if ext.lower() == '.txt' and \
       path.basename(fname).lower().startswith('cmake'):
        return ('CMake', '.txt', ('#', '# '))

    lang = ''
    tokens = ()
    ext = ext.lower()

    for fexts, ftype in _SOURCE_META.items():
        if not ext and filetype:
            meta = list(filter(lambda attrs: attrs.get(filetype.lower()),
                        ({ name.lower() : ftype[1] } for _, name in ftype[0].items())))
            if meta:
                lang, tokens = list(*meta[0].items())
                return (lang, ext, tokens)

        # keys of only one element will get expanded into a char sequence
        exts = [fexts] if fexts[0] == '.' else fexts
        if ext in exts:
            try:
                for grp in ftype[0]:
                    if (ext in grp and not grp[0] == '.') or \
                       (ext == grp and grp[0] == '.'):
                        lang = ftype[0][grp]
                        tokens = ftype[1]
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
    git_username = author

    try:
        git_username = check_output(['git',
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

    if bool(git_username):
        author = git_username
        email = ' <' + email + '>' if email else ''

    return (author, email)

_SOURCE_META = {
    ('', '.cmake', '.dockerfile', '.ex', '.exs', '.jl', '.mk', '.mak','.pl', '.py', '.pyw',
     '.conf', '.properties', '.r', '.rb', '.rda', '.rdata', '.rds', '.sh', '.yml', '.yaml'):
        [{
            ('.conf'): 'Config',
            ('.dockerfile'): 'Dockerfile',
            ('.ex', '.exs'): 'Elixir',
            ('.jl'): 'Julia',
            ('', '.sh'): 'shell script',
            ('.pl'): 'Perl',
            ('.py', '.pyw'): 'Python',
            ('.properties'): 'Properties',
            ('.r', '.rda', '.rdata', '.rds'): 'R',
            ('.rb'): 'Ruby',
            ('.yml', '.yaml'): 'YAML',
            ('.mk', '.mak'): 'Make',
            ('.cmake'): 'CMake'
        },
         ('#', '# ')],
    ('.bat', '.btm', '.cmd'):
        [{('.bat', '.btm', '.cmd'): 'Batch'}, ('::', ':: ')],
    ('.coffee', '.litcoffee'):
        [{('.coffee', '.litcoffee'): 'CoffeeScript'}, ('###', ' ', ' ', '###')],
    ('.asm', '.ini', '.s'):
        [{('.asm', '.s'): 'Assembly', ('.ini'): 'INI'}, (';', '; ')],
    ('.lisp', '.lsp', '.cl', '.scm', '.ss', '.clj', '.cljc', '.cljs', '.edn', '.fnl'):
        [{
            ('.lisp', '.lsp'): 'Lisp',
            ('.cl'): 'Common Lisp',
            ('.scm', '.ss'): 'Scheme',
            ('.clj', '.cljc'): 'Clojure',
            ('.cljs'): 'ClojureScript',
            ('.edn'): 'Edn',
            ('.fnl'): 'Fennel'
        },
         (';;', ';; ')],
    ('.erl', '.hrl', '.p', '.pro'):
        [{
            ('.erl'): 'Erlang',
            ('.hrl'): 'Erlang header',
            ('.p', '.pro'): 'Prolog'
        },
         ('%%', '%% ')],
    ('.c', '.cc', '.c++', '.cpp', '.cxx', '.cs', '.css', '.d', '.h', '.hh',
     '.h++', '.hpp', '.hxx', '.java', '.js', '.jsx', '.mjs', '.kt', '.kts',
     '.ktm', '.m', '.mm', '.php', '.php4', '.php5', '.phtml', '.re', '.rei',
     '.scala', '.sc', '.swift', '.ts', '.vala', '.vapi', '.cpp2', '.h2'):
        [{
            ('.c'): 'C source',
            ('.d'): 'D source',
            ('.h'): 'C header',
            ('.cc', '.c++', '.cpp', '.cxx'): 'C++ source',
            ('.hh', '.h++', '.hpp', '.hxx'): 'C++ header',
            ('.cpp2'): 'Cppfront source',
            ('.h2'): 'Cppfront header',
            ('.cs'): 'C-sharp',
            ('.css'): 'CSS',
            ('.java'): 'Java',
            ('.kt', '.kts', '.ktm'): 'Kotlin',
            ('.m', '.mm'): 'Objective-C',
            ('.php', '.php4', '.php5', '.phtml'): 'PHP',
            ('.js'): 'JavaScript',
            ('.jsx'): 'ReactJS',
            ('.mjs'): 'ES Module',
            ('.re', '.rei'): 'ReasonML',
            ('.scala', '.sc'): 'Scala',
            ('.swift'): 'Swift',
            ('.ts'): 'TypeScript',
            ('.vala', '.vapi'): 'Vala'
        },
         ('/**', ' * ', ' *', ' */')],
    ('.elm'):
        [{('.elm'): 'Elm'}, ('{-', ' ', ' ', '-}')],
    ('.dpk', '.dpr', '.lpr', '.ml', '.mli', '.pas', '.pp', '.inc'):
        [{
          ('.dpk', '.dpr', '.lpr', '.pas', '.pp', '.inc'): 'Pascal',
          ('.ml', '.mli'): 'OCaml'
         },
         ('(*', ' ', ' ', '*)')],
    ('.html', '.htm', '.markdown', '.md', '.mkd', '.xml'):
        [{('.html', '.htm'): 'HTML',
          ('.xml'): 'XML',
          ('.markdown', '.md', '.mkd'): 'Markdown'
         },
         ('<!--', ' ', ' ', '-->')],
    ('.rst'): [{('.rst'): 'reStructuredText'}, ('..', '.. ')],
    ('.adb', '.ads', '.e', '.lua', '.sql', '.hs', '.lhs', '.purs'):
        [{
            ('.adb', '.ads'): 'Ada',
            ('.e'): 'Eiffel',
            ('.lua'): 'Lua',
            ('.sql'): 'SQL',
            ('.hs', '.lhs'): 'Haskell',
            ('.purs'): 'PureScript'
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
    ('.st'):
        [{('.st'): 'Smalltalk'},
         ('"', ' ', ' ', '"')],
    ('.vim', '.vimrc', '.gvim', '.ideavim', '.exrc'):
        [{('.vim', '.vimrc', '.gvim', '.ideavim', '.exrc'): 'VimL'},
         ('""', '"" ')]
}
"""
Mapping of file extensions to comment markers for all programming languages
recognized by the Generator type
"""

_SCRIPT_HEADERS = {
    'shell script': '#!/usr/bin/env %s'
                    % re.sub(r'^\$\w+',
                             'bash',
                             path.expandvars('$SHELL').split('/')[-1]),
    'perl': '#!/usr/bin/env perl',
    'php': '<?php',
    'python': '#!/usr/bin/env python%s\n# -*- coding: utf-8 -*-\n'
              % sys.version_info[0],
    'ruby': '# frozen_string_literal: true\n',
}
"""
Header lines for the most common scripting languages
"""
