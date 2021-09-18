# -*- coding: utf-8 -*-

"""
Buffer manipulation functions
"""
from __future__ import print_function
import sys
import vim
from re import match
for path in vim.eval('globpath(&rtp,"rplugin/pythonx",1)').split('\n'):
    sys.path.append(path)
from cpywrite import Generator


def prepend():
    """Prepend license header to the open buffer"""
    if vim.current.buffer:
        vim.command("let b:fn=expand('%:t')")
        filename = vim.eval('b:fn')
        is_prolog = (filename.endswith('.pl') and vim.eval('&syntax') == 'prolog')
        license_name = vim.eval('l:license_name')

        try:
            generator = Generator(filename, license_name)

            if is_prolog:
                generator.set_file_props(filename.replace('.pl', '.p'))
                generator.out_file = filename

            _write_header(generator, vim.current.buffer)
        except (ValueError, vim.error) as exc:
            print(str(exc))
            return

def _write_header(writer, curr_buffer):
    """Write the license header"""
    try:
        old_row, old_col = vim.current.window.cursor
        machine_readable = _get_option_value('g:cpywrite#machine_readable')
        use_text_as_header = _get_option_value('g:cpywrite#verbatim_mode')
        exclude_file_name = _get_option_value('g:cpywrite#hide_filename')
        allow_anonymous = _get_option_value('g:cpywrite#no_anonymous')
        header = writer.fetch_license_header(use_text_as_header,
                                             machine_readable,
                                             exclude_file_name,
                                             allow_anonymous)

        if header:
            to_trim = 0
            offset = 0

            for idx, _ in enumerate(curr_buffer):
                # replace shebang lines and encoding declarations, if any
                if curr_buffer[idx].startswith("#!", 0) or \
                        match(r"^#.+(coding).+$", curr_buffer[idx]):
                    to_trim += 1
                # don't replace:
                # - Batch directives
                # - encoding or doctype declarations in [X|HT]ML,or
                #   existing PHP markup
                elif match(r"^\<[\?!]\w*", curr_buffer[idx].lstrip()) or \
                    match(r"\?*\>$", curr_buffer[idx].rstrip()) or \
                    match(r'^\@(echo )', curr_buffer[idx].lstrip()):
                    offset += 2

            if to_trim > 0:
                del curr_buffer[0:to_trim]

            curr_buffer[offset:offset] = header.split('\n')

    except (ValueError, vim.error) as exc:
        print(str(exc))
        vim.current.window.cursor = (old_row, old_col)
        return

def _get_option_value(vim_var):
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
