"" ==========================================================================
""   vim-cpywrite
""
""   Maintainer: Robert Di Pardo <dipardo.r@gmail.com>
""   URL:        https://github.com/rdipardo/vim-cpywrite
""   License:    MIT
"" ==========================================================================

if !has('python3')
    if !has('python')
        if has ('nvim')
            call health#report_error(
            \'Your editor is missing a python provider!',
            \ ['Enter :help provider-python for more information.'])
        else
            echohl WarningMsg |
                echom 'Error loading vim-cpywrite: this plugin requires one of
                \ the following features: +python, +python3, +python/dyn, or
                \ +python3/dyn. Enter :help python for more information.'
                \ | echohl None
        endif
    finish
    endif
endif

if get(g:, 'loaded_cpywrite') | finish | endif
let g:loaded_cpywrite = 1
let s:cpywrite_python_cmd = (has('python3') ? 'py3' : 'py') . 'file'

if !exists('g:cpywrite_version')
    exe s:cpywrite_python_cmd
        \ fnamemodify(
        \   globpath(&rtp, 'plugin/cpywrite/version.py', 0, 1)[0],
        \   ':p')
endif

if !exists('g:cpywrite_verbatim_mode')
    let g:cpywrite_verbatim_mode = 0
endif

if empty(get(g:, 'cpywrite_default_license', ''))
    let g:cpywrite_default_license = 'GPL-3.0-or-later'
endif

func! s:prepend_header(...) abort
    let l:license_name = get(a:, 1, g:cpywrite_default_license)
    exe s:cpywrite_python_cmd
        \ fnamemodify(
        \   globpath(&rtp, 'plugin/cpywrite/main.py', 0, 1)[0],
        \   ':p')
endfunc

func! s:get_license_list(a,l,p) abort
    let s:license_list=[]
    let l:subs = get(a:, 'a', '')
    exe s:cpywrite_python_cmd
        \ fnamemodify(
        \   globpath(&rtp, 'plugin/cpywrite/tabs.py', 0, 1)[0],
        \ ':p')

    return s:license_list
endfunc

func! s:set_default_license(...)
    if !empty(get(a:, 1, ''))
        exe 'let g:cpywrite_default_license = ' . string(a:1)
    endif

    exe 'echo g:cpywrite_default_license'
endfunc

if !exists(':CPYwrite')
    com! -nargs=* -complete=customlist,s:get_license_list
      \ CPYwrite :call s:prepend_header(<f-args>)
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
