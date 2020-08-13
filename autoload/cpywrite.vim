"" ==========================================================================
""   vim-cpywrite
""
""   Maintainer: Robert Di Pardo <dipardo.r@gmail.com>
""   URL:        https://github.com/rdipardo/vim-cpywrite
""   License:    MIT
"" ==========================================================================

if get(g:, 'autoloaded_cpywrite') | finish | endif
let g:autoloaded_cpywrite = 1

if has('python3') || has('python')
    if empty(get(s:, 'cpywrite_python_cmd', ''))
        let s:cpywrite_python_cmd = (has('python3') ? 'py3' : 'py') . 'file'
    endif

    if empty(get(g:, 'cpywrite_version', ''))
        exe s:cpywrite_python_cmd
          \ fnamemodify(
          \   globpath(&rtp, 'plugin/cpywrite/version.py', 0, 1)[0],
          \   ':p')
    endif
endif

func! cpywrite#PrependHeader(...) abort
    let l:loader = cpywrite#GetInterpreter()

    if empty(loader)
        call cpywrite#error#NoPython()
    else
        let l:license_name = get(a:, 1, g:cpywrite_default_license)
          exe loader
              \ fnamemodify(
              \   globpath(&rtp, 'plugin/cpywrite/main.py', 0, 1)[0],
              \   ':p')
    endif
endfunc

func! cpywrite#GetInterpreter()
    return exists('s:cpywrite_python_cmd') ? s:cpywrite_python_cmd : ''
endfunc
