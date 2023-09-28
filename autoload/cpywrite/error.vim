"" ==========================================================================
""   vim-cpywrite
""
""   Maintainer: Robert Di Pardo <dipardo.r@gmail.com>
""   URL:        https://github.com/rdipardo/vim-cpywrite
""   License:    MIT
"" ==========================================================================

if get(g:, 'autoloaded_cpywrite_error') | finish | endif
let g:autoloaded_cpywrite_error = 1

func! cpywrite#error#NoPython() abort
  let msg =
    \ 'Sorry: vim-cpywrite requires +python3 or +python3/dyn.
    \ Enter ":help python" for more information.'
  if has ('nvim')
      let msg =
        \ 'Your editor is missing a python provider!
        \ Enter :help provider-python for more information.'
  endif
  echohl WarningMsg | echom msg | echohl None
endfunc
