"" ==========================================================================
""   vim-cpywrite
""
""   Maintainer: Robert Di Pardo <dipardo.r@gmail.com>
""   URL:        https://github.com/rdipardo/vim-cpywrite
""   License:    MIT
"" ==========================================================================

if get(g:, 'loaded_cpywrite') | finish | endif
let g:loaded_cpywrite = 1

let g:cpywrite#version = '0.3.2-pre'

if empty(get(g:, 'cpywrite#default_license', ''))
    let g:cpywrite#default_license = 'GPL-3.0-or-later'
endif

if !exists('g:cpywrite#verbatim_mode')
    let g:cpywrite#verbatim_mode = 0
endif

if !exists('g:cpywrite#hide_filename')
    let g:cpywrite#hide_filename = 0
endif

if !exists(':CPYwrite')
    com! -nargs=* -complete=customlist,cpywrite#licenses#GetLicenseList
      \ CPYwrite :call cpywrite#PrependHeader(<f-args>)
endif

if !exists(':CPYwriteDefaultLicense')
    com! -nargs=* -complete=customlist,cpywrite#licenses#GetLicenseList
      \ CPYwriteDefaultLicense :call cpywrite#licenses#SetDefaultLicense(<f-args>)
endif

if !exists(':CPYwriteToggleMode')
    com! CPYwriteToggleMode
    \ exe 'if(g:cpywrite#verbatim_mode) | let g:cpywrite#verbatim_mode = 0 |
    \   else | let g:cpywrite#verbatim_mode = 1 | endif |
    \   echo (g:cpywrite#verbatim_mode) ? "verbatim" : "standard header/brief"'
endif

if !exists(':CPYwriteToggleFilename')
    com! CPYwriteToggleFilename
    \ exe 'if(g:cpywrite#hide_filename) | let g:cpywrite#hide_filename = 0 |
    \   else | let g:cpywrite#hide_filename = 1 | endif |
    \   echo (g:cpywrite#hide_filename) ? "hidden" : "showing"'
endif

nnoremap <silent> <Plug>(cpywrite)
    \ :exe 'CPYwrite ' . g:cpywrite#default_license . ' '<CR>

if !hasmapto('<Plug>(cpywrite)')
    nmap <unique> LH <Plug>(cpywrite)
endif
