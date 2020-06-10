# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from pytest import raises
from cpywrite.generator import Generator, _get_language_meta
from cpywrite import licenses


def test_language_recognition():
    c_lang_files = [
        'file.c', 'file.h', 'file.cc', 'file.CpP', 'file.c++', 'file.CxX',
        'file.hh', 'file.H++', 'file.hPp', 'file.cs', 'file.CsS', 'file.java',
        'file.JS', 'file.ts', 'file.pHp', 'file.phP4', 'file.Php5',
        'file.Phtml']
    lisp_lang_files = [
        'file.cl', 'file.lSp', 'file.LisP', 'file.cLJ', 'file.CLJC',
        'file.CLjS', 'file.sS', 'file.sCM']
    go_and_etc_files = [
        'file.gO', 'file.Rs', 'file.fs', 'file.fsi', 'file.fsx',
        'file.fsscript', 'file.sCsS']
    script_lang_files = [
        'script', 'script.Sh', 'script.pL', 'script.Py', 'script.Rb',
        'script.cMaKe']
    sql_and_haskell_files = ['file.sQl', 'file.HS', 'file.LhS']
    ml_lang_files = ['file.mL', 'file.MlI']
    html_files = ['file.hTmL', 'file.hTm']
    vim_script_files = ['script.viM', 'script.VIMrC']

    for src in c_lang_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('/**', ' * ', ' *', ' */')

    for src in lisp_lang_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == (';;', ';; ')

    for src in go_and_etc_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('//', '// ')

    for src in script_lang_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('#', '# ')

    for src in sql_and_haskell_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('--', '-- ')

    for src in ml_lang_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('(*', ' ', ' ', '*)')

    for src in html_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('<!--', ' ', ' ', '-->')

    for src in vim_script_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('""', '"" ')

def test_license_recognition():
    generator = Generator()

    for lic in licenses():
        generator.set_file_props('file.rb', lic)
        assert generator.rights.spdx_code == lic

def test_file_name_validation():
    invalid_file_names = [
        "", "wrong.", "wrong......", "w`rong.rb", "wr<ong.php", "wro>ng.ml",
        "w:rong.c++", "wron\\g.js", "wrong\\\".ts", "\\wrong.h", "w\\rong.hpp",
        "/wrong.hxx", "wro?ng.py", "wron*g.pl", "wron/g.html", "wron\\g.html"]
    generator = Generator()

    for fname in invalid_file_names:
        with raises(ValueError):
            generator.set_file_props(fname)
