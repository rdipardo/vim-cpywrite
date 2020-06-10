# vim-cpywrite

Generate copyright headers for any open source license

|    |
|:--:|
|<img src=".github/nvim_043_scheme.gif" alt="nvim-043-linux_demo" width="600"/>|

## Description

Mostly written in CPython, this (neo)vim plugin fetches the license of your choice directly from the [SPDX License List](https://github.com/spdx/license-list-xml). If the XML response contains a standard header, it's inserted at the top of the current buffer with your copyright info.

When no standard header is provided, you can either insert a brief license acknowledgement, or the full license text. (See the `g:cpywrite_verbatim_mode`  option [below](#quick-reference).)

This plugin learns your name and email by invoking `git`. If that fails, the copyright line will contain your OS user and host names.


## Highlights

- Python bindings compatible with python 2.7 or 3.4+, depending on your platform and (neo)vim version, of course
- Choose from 380 licenses (press `<tab>` after the `:CPYwrite` command for suggestions)
- No dependencies on other plugins. That said, neovim users will be grateful to have the [completeopt](https://neovim.io/doc/user/options.html#'completeopt') feature when tabbing through all the available licenses!


## Quick Reference
|   |   |
|:--|:--|
|`:CPYwrite [{spdx_short_name}]`|Fetches the license identified by `spdx_short_name` (without quotes) -- uses the current value of `g:cpywrite_default_license` when no argument is given -- supports `<tab>` completion |
|`<Plug>(cpywrite)`|Does the same as calling `:CPYwrite` with no argument|
|`{Normal}LH`|Maps to `<Plug>(cpywrite)`|
|`g:cpywrite_verbatim_mode`|When set to a "truthy" value, the full license text will be requested -- only choose this when the license is no longer than 3-4 paragraphs (e.g. Unlicense, MIT, BSD 1- 2- 3-Clause, etc.)|


## Requirements

* Vim compiled with any one of the *+python[3]* or *+python[3]/dyn* options. See if you're supported by entering `vim --version | grep +python` at your terminal, or start `vim` and enter the `:version` command

* neovim with the [**pynvim**](https://github.com/neovim/pynvim) module in your `$PYTHONPATH`. Start `nvim` and enter `:help provider-python` for more information


## Projects like this one

* [vim-licenses][vim-lic-2.0], formerly [licenses][vim-lic-1.0]
* [license-to-vim][lic2vim]
* [license loader][licl]


## TODO

- Provide a batch mode for licensing all tracked files in a working tree
- Expand the list of supported programming languages


## License

MIT


[vim-lic-2.0]: https://github.com/antoyo/vim-licenses
[vim-lic-1.0]: https://github.com/vim-scripts/Licenses
[lic2vim]: https://www.vim.org/scripts/script.php?script_id=5349
[licl]: https://www.vim.org/scripts/script.php?script_id=4064

<!--
 vim:ft=markdown:et:tw=78:
-->
