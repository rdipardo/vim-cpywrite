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
        license_name = vim.eval('l:license_name')

        try:
            generator = Generator(filename, license_name)
            _write_header(generator, vim.current.buffer)
        except (ValueError, vim.error) as exc:
            print(str(exc))
            return

def _write_header(writer, curr_buffer):
    """Write the license header"""
    try:
        old_row, old_col = vim.current.window.cursor
        use_text_as_header = vim.eval('g:cpywrite_verbatim_mode')

        try:
            use_text_as_header = bool(int(use_text_as_header, 10))
        except ValueError:
            print("'g:cpywrite_verbatim_mode' should be set to a number!",
                  file=sys.stderr)
            vim.command('let g:cpywrite_verbatim_mode=0')
            use_text_as_header = False

        header = writer.fetch_license_header(use_text_as_header)

        if header:
            to_trim = 0

            for idx, _ in enumerate(curr_buffer):
                # replace shebang lines and encoding declarations, if any
                if curr_buffer[idx].startswith("#!", 0) or \
                        match(r"^#.+(coding).+$", curr_buffer[idx]):
                    to_trim += 1

            if to_trim > 0:
                del curr_buffer[0:to_trim]

            curr_buffer[0:0] = header.split('\n')[:-1]

    except (ValueError, vim.error) as exc:
        print(str(exc))
        vim.current.window.cursor = (old_row, old_col)
        return


if __name__ == '__main__':
    prepend()
