# -*- coding: utf-8 -*-

"""
Tab completion
"""
import sys
import vim
from re import match, IGNORECASE
for path in vim.eval('globpath(&rtp, "rplugin/pythonx", 1)').split('\n'):
    sys.path.append(path)
from cpywrite import licenses


def match_license():
    """Retrieve license names matching user input"""
    try:
        subs = vim.eval('l:subs')
        matcher = lambda name: match(r'^(%s)' % subs, name, IGNORECASE)

        for lc_name in filter(matcher, licenses()):
            vim.command("call add(s:license_list, '%s')" % lc_name)
    except vim.error:
        pass


if __name__ == '__main__':
    match_license()
