### 0.2.0

- extract feature tests and core functions to `autoload` directory to [improve startup time][pr2]
- suggest [`set wildmenu`](README.md#highlights) for faster completions when not using neovim

### 0.1.1

- convenience commands for getting/setting global options:
    - `:CPYwriteDefaultLicense` -- supports `<tab>` completion
    - `:CPYwriteToggleMode` -- switches `g:cpywrite_verbatim_mode` on/off

- relaxed file naming rules to accept full paths

- recognize *CMakeLists* files with the `.txt` extension

- apply line wrapping to keep standard headers within 80 chars (still in progress; expect mixed results)

- brief notices are now fully capitalized

- better-looking standard headers for the older GPL and GFDL licenses families

### 0.1.0

- initial release


[pr2]: https://github.com/rdipardo/vim-cpywrite/pull/2

