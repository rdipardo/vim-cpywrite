# -*- coding: utf-8 -*-

"""
Buffer manipulation functions
"""
import sys
import os
import vim
from re import match, sub
for path in vim.eval('globpath(&rtp,"rplugin/python3",1)').split('\n'):
    sys.path.append(path)
from cpywrite.spdx.license import License
from cpywrite.generator import Generator, _get_source_author


def prepend():
    """Prepend license header to the open buffer"""
    if vim.current.buffer:
        vim.command("let b:fn=expand('%:t')")
        filename = vim.eval('b:fn')
        filetype = vim.eval('&syntax')
        license_name = vim.eval('l:license_name')

        try:
            generator = Generator(filename, filetype, license_name)

            if (filename.endswith('.pl') and filetype == 'prolog'):
                generator.set_file_props(filename.replace('.pl', '.p'), filetype)
                generator.out_file = filename

            _write_header(generator, vim.current.buffer, filetype, filename)
        except ValueError: # try falling back to buffer's file type attributes
            tokens = list(map(str.strip, vim.eval('&commentstring').split('%s')))
            if not tokens or not tokens[0]:
                return
            try:
                generator = Generator(os.path.splitext(filename)[0])
                if len(tokens) == 1 or not tokens[1]:
                    generator.tokens = (tokens[0], tokens[0] + '\x20')
                else:
                    generator.tokens = (tokens[0], '\x20', '\x20', tokens[1])
                generator.rights = License(license_name)
                generator.lang = filetype
                generator.out_file = filename
                _write_header(generator, vim.current.buffer, filetype, filename)
            except ValueError as exc:
                raise vim.error from exc
        except vim.error as exc:
            print(str(exc))
            return

def _write_header(writer, curr_buffer, filetype, filename):
    """Write the license header"""
    try:
        old_row, old_col = vim.current.window.cursor
        machine_readable = _get_option_value('g:cpywrite#machine_readable')
        use_text_as_header = _get_option_value('g:cpywrite#verbatim_mode')
        exclude_file_name = _get_option_value('g:cpywrite#hide_filename')
        allow_anonymous = _get_option_value('g:cpywrite#no_anonymous')
        preserve_shebangs = _get_option_value('g:cpywrite#preserve_shebangs')
        include_javadoc = _get_option_value('g:cpywrite#java#add_class_doc')
        header = writer.fetch_license_header(use_text_as_header,
                                             machine_readable,
                                             exclude_file_name,
                                             allow_anonymous)

        if header:
            to_trim = 0
            to_skip = 0
            offset = 0

            for idx, _ in enumerate(curr_buffer):
                curr_line = curr_buffer[idx].lstrip()
                is_script = curr_line.startswith("#!", 0) or \
                        match(r"^#.+(coding).+$", curr_line)
                # replace shebang lines and encoding declarations, if any
                if not preserve_shebangs and is_script:
                    to_trim += 1
                # don't replace:
                # - encoding or doctype declarations in [X|HT]ML,or
                # - existing PHP markup
                # - Batch directives
                elif match(r"^\<[\?!]\w*", curr_line) or \
                    match(r"\?*\>$", curr_buffer[idx].rstrip()) or \
                    (filetype == 'dosbatch' and curr_line.startswith('@', 0)):
                    offset += 2
                elif preserve_shebangs and is_script:
                    offset = (offset + 1) if len(curr_line) > 0 else offset
                    # make an exception for Ruby because we don't insert a shebang,
                    # and never will: it upsets rubocop if the exec perm flag is not
                    # set; the `--safe-auto-correct` option will actually *make* the
                    # file executable(!)
                    # https://docs.rubocop.org/rubocop/cops_lint.html#lintscriptpermission
                    to_skip = (to_skip + 1) if filetype != 'ruby' else to_skip

                if include_javadoc:
                    class_name, _ = os.path.splitext(filename)

                    if curr_line.find(class_name) > -1:
                        class_doc = idx
                        docline = curr_buffer[class_doc]

                        while class_doc > 0 and docline.find('/**') == -1:
                            class_doc -= 1
                            docline = curr_buffer[class_doc]

                        # insert tag into existing doc comment only
                        if docline.find('/**') > -1:
                            class_doc += 1
                            docline = curr_buffer[class_doc]

                            while class_doc < len(curr_buffer) and \
                                    not match(r'^\s*.*\*\/', docline):
                                # doc line must be blank
                                if match(r'^\s*\*+\s*$', docline):
                                    author, email = _get_source_author()
                                    email = sub(r'\<', '&lt;', sub(r'\>', '&gt;', email))
                                    curr_buffer[class_doc:class_doc] = \
                                        [docline, '%s @author %s %s' % (docline, author, email)]

                                    break
                                else:
                                    class_doc += 1
                                    docline = curr_buffer[class_doc]

                        break

            if to_trim > 0:
                del curr_buffer[0:to_trim]

            curr_buffer[offset:offset] = header.splitlines()[to_skip:]

    except (ValueError, vim.error) as exc:
        print(str(exc))
        vim.current.window.cursor = (old_row, old_col)
        return

def _get_option_value(vim_var):
    if vim.vars.get(sub(r'[abglsv]:', '', vim_var)) is None:
        return False

    try:
        val = bool(int(vim.eval(vim_var), 10))
    except ValueError:
        print("'%s' should be set to a number!" % vim_var,
              file=sys.stderr)
        vim.command('let %s=0' % vim_var)
        val = False

    return val


if __name__ == '__main__':
    prepend()
