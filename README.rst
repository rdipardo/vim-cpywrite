############
vim-cpywrite
############

|gh-actions|  |coverage|  |current version|

Generate copyright headers for any open source license

.. figure:: https://raw.githubusercontent.com/rdipardo/vim-cpywrite/media/rel/vim_8.2.4046.gif
    :alt: vim-win-x64-demo
    :align: center
    :width: 900

----

.. contents:: **Contents**
    :depth: 2
    :backlinks: top

Introduction
============

Mostly written in CPython, this (neo)vim plugin fetches the license of your
choice directly from the `SPDX License List`_. If the XML response contains a
standard header, it's inserted at the top of the current buffer with your
copyright info.

When no standard header is provided, you can either insert a brief license
acknowledgment, or the full license text. (See the ``g:cpywrite#verbatim_mode``
option `below <#options>`_.)

This plugin learns your name and email by invoking ``git``. If that fails, the
copyright line will contain your OS user and host names.

.. _SPDX License List: https://github.com/spdx/license-list-xml

Features
========

* Python bindings compatible with python 3.7+, depending on your
  platform and (neo)vim version, of course

:NOTE: Python 3.10 requires `neovim 0.6.0`_ or newer.
       All vim versions from 7.4 and up should be compatible.
       `Bug reports <https://github.com/rdipardo/vim-cpywrite/issues>`_ are welcome.

* Choose from more than 420 licenses (press ``<tab>`` after the ``:CPYwriteDefaultLicense``
  or ``:CPYwrite`` command for suggestions)

.. _completions:

* No dependency on other plugins. That said, neovim users will be grateful to
  have the `completeopt`_ feature when tabbing through all the available
  licenses. Vim users may want to add ``set wildmenu`` to their ``.vimrc`` file

.. _completeopt: https://neovim.io/doc/user/options.html#'completeopt'
.. _`neovim 0.6.0`: https://github.com/neovim/neovim/commit/e65b724451ba5f65dfcaf8f8c16afdd508db7359

Quick Reference
===============

Commands
--------
+------------------------------------------------+---------------------------------------------+
|``:CPYwrite [{spdx_short_name}]``               | Fetches the license identified by           |
|                                                | ``spdx_short_name`` (without quotes) --     |
|                                                | uses the current value of                   |
|                                                | ``g:cpywrite#default_license`` when no      |
|                                                | argument is given -- supports ``<tab>``     |
|                                                | completion                                  |
+------------------------------------------------+---------------------------------------------+
|``:CPYwriteDefaultLicense [{spdx_short_name}]`` | Sets ``g:cpywrite#default_license`` to the  |
|                                                | license identified by ``spdx_short_name``   |
|                                                | (without quotes) -- prints the default      |
|                                                | licence id when called with no argument --  |
|                                                | supports ``<tab>`` completion               |
+------------------------------------------------+---------------------------------------------+
|``:CPYwriteKeepShebangs``                       | Switches ``g:cpywrite#preserve_shebangs``   |
|                                                | on or off                                   |
+------------------------------------------------+---------------------------------------------+
|``:CPYwriteToggleMode``                         | Switches ``g:cpywrite#verbatim_mode`` on or |
|                                                | off                                         |
+------------------------------------------------+---------------------------------------------+
|``:CPYwriteToggleStyle``                        | Switches ``g:cpywrite#machine_readable`` on |
|                                                | or off                                      |
+------------------------------------------------+---------------------------------------------+
|``:CPYwriteToggleFilename``                     | Switches ``g:cpywrite#hide_filename`` on or |
|                                                | off                                         |
+------------------------------------------------+---------------------------------------------+
|``:CPYwriteAllowAnonymous``                     | Switches ``g:cpywrite#no_anonymous`` on or  |
|                                                | off                                         |
+------------------------------------------------+---------------------------------------------+
|``<Plug>(cpywrite)``                            | Does the same as calling ``:CPYwrite`` with |
|                                                | no argument                                 |
+------------------------------------------------+---------------------------------------------+

Default mappings
----------------
+----------------+------------------------------+
| ``{Normal}LH`` | Maps to ``<Plug>(cpywrite)`` |
+----------------+------------------------------+

Options
-------
+----------------------------------+-----------------------------------------------+
| ``g:cpywrite#default_license``   | The SPDX identifier of the license to be      |
|                                  | fetched by the ``:CPYwrite`` command.         |
|                                  | Default: ``'Apache-2.0'``                     |
+----------------------------------+-----------------------------------------------+
| ``g:cpywrite#preserve_shebangs`` | When set to a non-zero value, the license     |
|                                  | header is inserted *after* any shebang or     |
|                                  | encoding directive (since `0.7.0`_).          |
|                                  | Default: ``1``                                |
+----------------------------------+-----------------------------------------------+
| ``g:cpywrite#verbatim_mode``     | When set to a non-zero value, the full        |
|                                  | license text will be requested -- you should  |
|                                  | only choose this when the license is no       |
|                                  | longer than 3-4 paragraphs (e.g. Unlicense,   |
|                                  | MIT, BSD 1- 2- 3-Clause, etc.).               |
|                                  | Default: ``0``                                |
+----------------------------------+-----------------------------------------------+
| ``g:cpywrite#no_anonymous``      | When set to a non-zero value, copyright       |
|                                  | information is never omitted, even if the     |
|                                  | license implies a Public Domain grant.        |
|                                  | Default: ``0``                                |
+----------------------------------+-----------------------------------------------+
|                                  | Has no effect when                            |
|                                  | ``g:cpywrite#machine_readable`` is on         |
+----------------------------------+-----------------------------------------------+
| ``g:cpywrite#machine_readable``  | When set to a non-zero value, the license     |
|                                  | and copyright statement are formatted as      |
|                                  | tags.                                         |
|                                  | Default: ``0``                                |
+----------------------------------+-----------------------------------------------+
|                                  | Overrides ``g:cpywrite#verbatim_mode`` and    |
|                                  | ``g:cpywrite#no_anonymous``                   |
+----------------------------------+-----------------------------------------------+
| ``g:cpywrite#hide_filename``     | When set to a non-zero value, hides the name  |
|                                  | of the current buffer from the license header |
|                                  | in all modes.                                 |
|                                  | Default: ``0``                                |
+----------------------------------+-----------------------------------------------+
| ``g:cpywrite#java#add_class_doc``| When set to a non-zero value, ``:CPYwrite``   |
|                                  | will try to insert an appropriate ``@author`` |
|                                  | tag into an existing JavaDoc comment above    |
|                                  | the main class definition.                    |
|                                  | Default: ``1`` (file type must be ``java``)   |
+----------------------------------+-----------------------------------------------+

.. _`0.7.0`: https://github.com/rdipardo/vim-cpywrite/blob/master/CHANGELOG.rst#changes-in-070

Requirements
============

* Vim compiled with any one of the *+python3* or *+python3/dyn* options.
  See if you're supported by entering ``vim --version | grep +python3`` at your
  terminal, or start ``vim`` and enter the ``:version`` command

* Neovim with the `pynvim`_ module in your ``$PYTHONPATH``. Start ``nvim``
  and enter ``:help provider-python`` for more information

.. _pynvim: https://github.com/neovim/pynvim

Installation
============

If `pynvim`_ is not already in your ``$PYTHONPATH``, install it::

    pip install --user -U pynvim


As a vim package
----------------

If you have vim 8+, you can directly copy the plugin source tree to your
`native package directory`_::

    git clone https://github.com/rdipardo/vim-cpywrite ~/.vim/pack/*/start/vim-cpywrite

**Note.** You can replace ``*`` with any name you want (e.g. ``plugins``)

Learn more by typing ``:help packages`` into your ``vim`` command prompt.
You should also read about `DIY plugin management`_.

Users of older vim versions can simulate native package loading with `vim-pathogen`_.

As a remote plugin
------------------

Using `plug.vim <https://github.com/junegunn/vim-plug>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Edit your ``~/.vimrc``, ``~/.vim/vimrc``, or ``~/.config/nvim/init.vim``:

.. code-block:: vim

    call plug#begin('~/path/to/your/plugin/directory/')

    Plug 'rdipardo/vim-cpywrite'

    call plug#end()


Using `Vundle <https://github.com/VundleVim/Vundle.vim>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install Vundle::

    git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim

or (if using neovim)::

    git clone https://github.com/VundleVim/Vundle.vim.git ~/.config/nvim/bundle/Vundle.vim

Edit your ``~/.vimrc``, ``~/.vim/vimrc``, or ``~/.config/nvim/init.vim``:

.. code-block:: vim

    set rtp+=~/.vim/bundle/Vundle.vim
    "or:
    "set rtp+=~/.config/nvim/bundle/Vundle.vim

    call vundle#begin()

    Plugin 'rdipardo/vim-cpywrite'

    call vundle#end()


Projects like this one
======================

* vim-copyright_ (*not* a fork)
* vim-licenses_, formerly licenses_
* vim-header_
* license-to-vim_
* `license loader`_

.. _vim-copyright: https://github.com/nine2/vim-copyright
.. _vim-licenses: https://github.com/antoyo/vim-licenses
.. _licenses: https://github.com/vim-scripts/Licenses
.. _vim-header: https://github.com/alpertuna/vim-header
.. _license-to-vim: https://www.vim.org/scripts/script.php?script_id=5349
.. _license loader: https://www.vim.org/scripts/script.php?script_id=4064

TODO
====

|_| Provide a batch mode for licensing all tracked files in a working tree

|_| Provide the option to set user-defined authorship details

|x| Expand the list of `supported programming languages`_

.. |_| unicode:: U+2610 .. BALLOT BOX
.. |X| unicode:: U+2611 .. BALLOT BOX WITH CHECK

Improve this README
-------------------

Consider opening a PR with an updated `installation guide <#installation>`_ if any of the
following applies to you:

* installation fails
* installation succeeds with a plugin manager not mentioned here

License
=======

Distributed under the terms of the MIT license.

.. |gh-actions| image:: https://github.com/rdipardo/vim-cpywrite/workflows/(Neo)vim/badge.svg?branch=pre-release
    :alt: Build Status
    :target: https://github.com/rdipardo/vim-cpywrite/actions
.. |current version| image:: https://img.shields.io/github/v/release/rdipardo/vim-cpywrite?logo=vim
    :alt: Vim Scripts version
.. |coverage| image:: https://codecov.io/gh/rdipardo/vim-cpywrite/graph/badge.svg
    :alt: Coverage stats
    :target: https://codecov.io/gh/rdipardo/vim-cpywrite

.. _supported programming languages: https://github.com/rdipardo/vim-cpywrite/blob/4d99f7af6a54442055e2c17a3ee12258623b64e9/rplugin/pythonx/cpywrite/generator.py#L320
.. _vim-pathogen: https://github.com/tpope/vim-pathogen#native-vim-package-management
.. _native package directory: https://github.com/vim/vim/blob/03c3bd9fd094c1aede2e8fe3ad8fd25b9f033053/runtime/doc/repeat.txt#L515
.. _DIY plugin management: https://shapeshed.com/vim-packages

.. vim:ft=rst:et:tw=78:
