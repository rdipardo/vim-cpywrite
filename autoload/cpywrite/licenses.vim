"" ==========================================================================
""   vim-cpywrite
""
""   Maintainer: Robert Di Pardo <dipardo.r@gmail.com>
""   URL:        https://github.com/rdipardo/vim-cpywrite
""   License:    MIT
"" ==========================================================================

if get(g:, 'autoloaded_cpywrite_licenses') | finish | endif
let g:autoloaded_cpywrite_licenses = 1

func! cpywrite#licenses#SetDefaultLicense(...) abort
    if !empty(get(a:, 1, ''))
        exe 'let g:cpywrite#default_license = ' . string(a:1)
    endif

    exe 'echo g:cpywrite#default_license'
endfunc

func! cpywrite#licenses#GetLicenseList(a,l,p) abort
    let l:loader = cpywrite#GetInterpreter()
    let s:license_list = []

    if empty(loader)
      call cpywrite#error#NoPython()
    else
        let l:subs = get(a:, 'a', '')
        exe loader
            \ fnamemodify(
            \   globpath(&rtp, 'plugin/cpywrite/tabs.py', 0, 1)[0],
            \ ':p')
    endif

    return s:license_list
endfunc
