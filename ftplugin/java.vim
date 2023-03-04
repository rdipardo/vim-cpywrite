"" ==========================================================================
""   This filetype plugin is part of vim-cpywrite
""
""   Maintainer: Robert Di Pardo <dipardo.r@gmail.com>
""   URL:        https://github.com/rdipardo/vim-cpywrite
""   License:    MIT
"" ==========================================================================

if exists('b:ftplugin_loaded') | finish | endif
let b:ftplugin_loaded = 1

if !exists('g:cpywrite#java#add_class_doc')
    let g:cpywrite#java#add_class_doc = 1
endif
