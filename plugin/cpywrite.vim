"" ==========================================================================
""   vim-cpywrite
""
""   Maintainer: Robert Di Pardo <dipardo.r@gmail.com>
""   URL:        https://github.com/rdipardo/vim-cpywrite
""   License:    MIT
"" ==========================================================================

if get(g:, 'loaded_cpywrite') | finish | endif
let g:loaded_cpywrite = 1

let g:cpywrite#version = '0.8.3-pre'

if empty(get(g:, 'cpywrite#default_license', ''))
    let g:cpywrite#default_license = 'Apache-2.0'
endif

if !exists('g:cpywrite#machine_readable')
    let g:cpywrite#machine_readable = 0
endif

if !exists('g:cpywrite#verbatim_mode')
    let g:cpywrite#verbatim_mode = 0
endif

if !exists('g:cpywrite#hide_filename')
    let g:cpywrite#hide_filename = 0
endif

if !exists('g:cpywrite#no_anonymous')
    let g:cpywrite#no_anonymous = 0
endif

if !exists('g:cpywrite#preserve_shebangs')
    let g:cpywrite#preserve_shebangs = 1
endif

if !exists(':CPYwrite')
    com! -nargs=* -complete=customlist,cpywrite#licenses#GetLicenseList
      \ CPYwrite :call cpywrite#PrependHeader(<f-args>)
endif

if !exists(':CPYwriteDefaultLicense')
    com! -nargs=* -complete=customlist,cpywrite#licenses#GetLicenseList
      \ CPYwriteDefaultLicense :call cpywrite#licenses#SetDefaultLicense(<f-args>)
endif

if !exists(':CPYwriteToggleStyle')
    com! CPYwriteToggleStyle
    \ exe 'let g:cpywrite#machine_readable = !g:cpywrite#machine_readable |
    \   echo (g:cpywrite#machine_readable) ? "machine readable" : "descriptive"'
endif

if !exists(':CPYwriteToggleMode')
    com! CPYwriteToggleMode
    \ exe 'let g:cpywrite#verbatim_mode = !g:cpywrite#verbatim_mode |
    \   echo (g:cpywrite#verbatim_mode) ? "verbatim" : "standard header/brief"'
endif

if !exists(':CPYwriteToggleFilename')
    com! CPYwriteToggleFilename
    \ exe 'let g:cpywrite#hide_filename = !g:cpywrite#hide_filename |
    \   echo (g:cpywrite#hide_filename) ? "hidden" : "showing"'
endif

if !exists(':CPYwriteAllowAnonymous')
    com! CPYwriteAllowAnonymous
    \ exe 'let g:cpywrite#no_anonymous = !g:cpywrite#no_anonymous |
    \   echo (g:cpywrite#no_anonymous) ? "never" : "Public Domain only"'
endif

if !exists(':CPYwriteKeepShebangs')
    com! CPYwriteKeepShebangs
    \ exe 'let g:cpywrite#preserve_shebangs = !g:cpywrite#preserve_shebangs |
    \   echo (g:cpywrite#preserve_shebangs) ? "preserve existing" : "overwrite"'
endif

nnoremap <silent> <Plug>(cpywrite)
    \ :exe 'CPYwrite ' . g:cpywrite#default_license . ' '<CR>

if !hasmapto('<Plug>(cpywrite)')
    nmap <unique> LH <Plug>(cpywrite)
endif
