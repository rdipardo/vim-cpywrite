#########
CHANGELOG
#########

.. contents:: **Releases**
   :depth: 1
   :backlinks: top

0.3.0
======
**(2020-10-12)**

Changed
-------
- options that were prefixed with ``cpywrite_`` now start with ``cpywrite#``;
  this will allow future new options to be loaded from the ``autoload``
  directory
- licenses are now identified by full name when there's no standard header

.. _configure vim to wrap lines:

**Note.** To keep longer names like (e.g.) the ``LGPLvX.X`` from running off
the screen, enable line wrapping in your ``vimrc`` or ``init.vim``:

.. code-block:: vim

    set lbr
    set tw=500 "break after 500 characters
    set wrap "wrap lines

Added
-----
- HTTP responses are now `cached`_ in the user's temp directory
- the option to hide the current buffer's name in license headers by setting
  ``g:cpywrite#hide_filename`` to a non-zero value
- a ``:CPYwriteToggleFilename`` command for setting the above option
- detect ``.vimrc``, ``.gvim``, ``.ideavim`` and ``.exrc`` as Vim files
- support for these file types:

  + D
  + Edn (.edn)
  + Fennel
  + Markdown
  + ReactJS (.jsx) and ES Module (.mjs)
  + Scala
  + Swift


0.2.1
=====
**(2020-08-16)**

Fixed
-----
- improve load time of ``autoload/cpywrite.vim``
- refactor regex that was inserting authorship at random places in full
  license text

Added
-----
- recognize ``.vimrc`` as VimL
- prevent copyright notice for appearing on public domain (i.e. copyright-free)
  licenses, in both modes
- leave one blank line after header
- support for these file types:

  + Ada
  + Assembler
  + Coffescript
  + Elixir
  + Elm
  + Erlang
  + Kotlin
  + Lua
  + Objective-C
  + Pascal


0.2.0
=====
**(2020-08-13)**

Fixed
-----
- extract feature tests and core functions to ``autoload`` directory to improve
  startup time (`#2`_)

Added
-----
- document suggestion to use `set wildmenu`_  for faster completions when not
  using neovim

.. _`set wildmenu`: README.rst#completions


0.1.1
=====
**(2020-07-25)**

Fixed
-----
- brief notices are now fully capitalized
- better-looking standard headers for the older GPL and GFDL licenses families

Added
-----
- convenience commands for getting/setting global options:

  + ``:CPYwriteDefaultLicense`` -- supports ``<tab>`` completion
  + ``:CPYwriteToggleMode`` -- switches ``g:cpywrite#verbatim_mode`` on/off

- relaxed file naming rules to accept full paths
- recognize *CMakeLists* files with the ``.txt`` extension
- apply line wrapping to keep standard headers within 80 chars (you should
  still `configure vim to wrap lines`_ for best results)


0.1.0
=====
**(2020-06-18)**

- initial release


.. _`#2`: https://github.com/rdipardo/vim-cpywrite/pull/2
.. _cached: https://github.com/rdipardo/vim-cpywrite/blob/7661fb2a6d1cf81b949f2ec9854c9598c04fac4a/rplugin/pythonx/cpywrite/spdx/license.py#L55

.. vim:ft=rst:et:tw=78:
