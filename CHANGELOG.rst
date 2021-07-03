#########
CHANGELOG
#########

.. contents:: **Releases**
   :depth: 1
   :backlinks: top

0.5.0
======
**(2021-07-03)**

Fixed
-----
- fallback to a system user name if no git email exists

Changed
-------
- preserve existing markup, encoding and doctype declarations at the top of
  XML, HTML or PHP files

Added
-----
- support for these file types:

  + Julia
  + Prolog (detected by ``&syntax`` when the extension is ``*.pl``)
  + XML

0.4.0
======
**(2021-05-24)**

Fixed
-----
- include user's email in the ECL-1.0 header

Changed
-------
- the initial value of ``g:cpywrite#default_license`` is now ``'Apache-2.0'``
- drop the `deprecated FreeBSD variant`_ of the BSD 2-Clause License
- detect more styles of authorship template, like a generic range years
  (e.g. ``<yyyy, yyyy>``), or an actual year that's merely historical
  (e.g. copyright notice of the 0BSD). The old matching rules are retained
  for the licenses that need them (e.g. the GFDLs, the ECLs, etc.)

.. _deprecated FreeBSD variant: https://spdx.org/licenses/BSD-2-Clause-FreeBSD

Added
-----
- include recent additions to the `SPDX License List`_

.. _SPDX License List: https://spdx.org/licenses

0.3.4
======
**(2021-04-04)**

Fixed
-----
- prevent copyright year regex from accidentally matching older versions of the
  Mozilla Public License
- don't throw an exception if the full name of a license doesn't start with *The*
- don't print angle brackets when ``user.email`` is empty

Changed
-------
- try to detect the user's interpreter program when modifying a shell script
- remove example GIF from plugin assets and use a hyperlink instead

0.3.3
======
**(2021-03-08)**

Fixed
-----
- (temporarily) request *ALL* full text licenses from the `previous release versions`_
  (with the exception of the `Unlicense`_ and `BSD-1-Clause`_ as before). A future
  release will probably start using a different repository when these versions
  fall too far behind the officially recognized templates
- minor refactoring of some redundant code

.. _previous release versions: https://github.com/spdx/license-list-data/releases/tag/v3.11

0.3.2
======
**(2020-12-28)**

Fixed
-----
- replace double-quotes with single-quotes when filetypes use ``"`` as their
  comment delimiter (i.e. VimL, Smalltalk)
- (temporarily) avoid requesting defective copies of the full `Unlicense`_ and
  `BSD-1-Clause`_
- minor pruning of some unreachable code (overlooked in `last release`_)

.. _last release: https://github.com/rdipardo/vim-cpywrite/blob/master/CHANGELOG.rst#031

Added
-----
- match the ``.mkd`` extension with Markdown files
- support for these file types:

  + Eiffel
  + PureScript
  + R
  + ReasonML
  + Smalltalk
  + Vala

0.3.1
======
**(2020-10-26)**

Changed
-------
- use reStructuredText in project documentation

Fixed
-----
- call ``re.escape()`` on emails when searching authorship templates in case
  they contain regex symbols, e.g. ``00000000+some1@users.noreply.github.com``


0.3.0
======
**(2020-10-12)**

Changed
-------
- options that were prefixed with ``cpywrite_`` now start with ``cpywrite#``;
  this will allow future options to be loaded from the ``autoload`` directory

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
.. _Unlicense: https://github.com/spdx/license-list-data/blob/2e20899c0504ff6c0acfcc1b0994d7163ce46939/text/Unlicense.txt#L10
.. _BSD-1-Clause: https://github.com/spdx/license-list-data/blob/2e20899c0504ff6c0acfcc1b0994d7163ce46939/text/BSD-1-Clause.txt#L9

.. vim:ft=rst:et:tw=78:
