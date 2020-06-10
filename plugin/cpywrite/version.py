# -*- coding: utf-8 -*-

"""
Expose plugin version
"""
import sys
import vim
for path in vim.eval('globpath(&rtp, "rplugin/pythonx", 1)').split('\n'):
    sys.path.append(path)
from cpywrite import __version__


def get_plugin_version():
    """Retrieve the version number of this plugin"""
    try:
        vim.command("let g:cpywrite_version = printf('%s', '" + \
                    __version__ + "')")
    except vim.error:
        pass


if __name__ == '__main__':
    get_plugin_version()
