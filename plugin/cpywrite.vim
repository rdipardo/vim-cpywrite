"" ==========================================================================
""   vim-cpywrite
""
""   Maintainer: Robert Di Pardo <dipardo.r@gmail.com>
""   URL:        https://github.com/rdipardo/vim-cpywrite
""   License:    MIT
"" ==========================================================================

if get(g:, 'loaded_cpywrite') | finish | endif
let g:loaded_cpywrite = 1

let g:cpywrite_version = '0.2.1-pre'

if empty(get(g:, 'cpywrite_default_license', ''))
    let g:cpywrite_default_license = 'GPL-3.0-or-later'
endif

if !exists('g:cpywrite_verbatim_mode')
    let g:cpywrite_verbatim_mode = 0
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
    \ exe 'if(g:cpywrite_verbatim_mode) | let g:cpywrite_verbatim_mode = 0 |
    \   else | let g:cpywrite_verbatim_mode = 1 | endif |
    \   echo (g:cpywrite_verbatim_mode) ? "verbatim" : "standard header/brief"'
endif

if !exists(':CPYwriteDefaultLicense')
    com! -nargs=* -complete=customlist,s:get_license_list
      \ CPYwriteDefaultLicense :call s:set_default_license(<f-args>)
endif

if !exists(':CPYwriteToggleMode')
    com! CPYwriteToggleMode
    \ exe 'if(g:cpywrite_verbatim_mode) | let g:cpywrite_verbatim_mode = 0 |
    \   else | let g:cpywrite_verbatim_mode = 1 | endif |
    \   echo (g:cpywrite_verbatim_mode) ? "verbatim" : "standard header/brief"'
endif

nnoremap <silent> <Plug>(cpywrite)
    \ :exe 'CPYwrite ' . g:cpywrite_default_license . ' '<CR>

if !hasmapto('<Plug>(cpywrite)')
    nmap <unique> LH <Plug>(cpywrite)
endif
