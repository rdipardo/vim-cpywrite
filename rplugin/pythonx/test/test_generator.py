# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from pytest import raises
from cpywrite.generator import Generator, _get_language_meta
from cpywrite import licenses


def test_language_recognition():
    c_lang_files = [
        'file.c', 'file.h', 'file.cc', 'file.CpP', 'file.c++', 'file.CxX',
        'filed.D', 'file.hh', 'file.H++', 'file.hPp', 'file.cs', 'file.CsS',
        'file.java', 'file.KT', 'file.kTs', 'file.Ktm', 'file.M', 'file.mM',
        'file.sWiFt', 'file.VAlA', 'file.vAPi']
    web_lang_files = [
        'file.JS', 'file.jSx', 'module.MjS', 'file.ts', 'file.pHp',
        'file.phP4', 'file.Php5', 'file.Phtml', 'file.Re', 'file.Rei']
    assembly_lang_files = ['file.S', 'file.s', 'fils.Asm']
    lisp_lang_files = [
        'file.cl', 'file.lSp', 'file.LisP', 'file.cLJ', 'file.CLJC',
        'file.CLjS', 'file.sS', 'file.sCM', 'deps.Edn', 'file.FNl']
    erlang_files = ['file.Erl', 'file.hRl']
    prolog_files = ['file.pRO', 'file.P']
    pascal_files = ['file.PAs', 'file.pP', 'file.iNC']
    scala_files = ['file.sCaLa', 'file.SCala', 'file.sC']
    go_and_etc_files = [
        'file.gO', 'file.Rs', 'file.fs', 'file.fsi', 'file.fsx',
        'file.fsscript', 'file.sCsS']
    script_lang_files = [
        'script', 'script.eX', 'script.ExS', 'script.Sh', 'script.jL',
        'script.pL', 'script.Py', 'script.PyW', 'script.R', 'script.rDA',
        'script.RdAta', 'script.rdS', 'script.Rb', 'script.cMaKe',
        'CMakeLists.tXt']
    coffeescript_files = ['file.coFFee', 'main.litcoffEe']
    elm_files = ['file.eLm', 'file.Elm', 'file.elM']
    ml_lang_files = ['file.mL', 'file.MlI']
    markup_files = ['file.hTmL', 'file.hTm', 'file.MaRkDoWn', 'file.MD',
                    'file.mKd', 'file.XmL']
    vim_script_files = [
        'script.viM', '.VIMrC', 'config.VIMrC', '.gvim', 'config.gvim',
        '.ideavim', 'script.ideavim', '.exrc', 'config.exrc']
    misc_script_files = [
        'file.ADb', 'file.adS', 'file.E', 'file.LuA', 'file.sQl',
        'file.HS', 'file.LhS', 'file.PuRs']
    smalltalk_files = ['class.sT', 'instance.St']

    for src in c_lang_files + web_lang_files + scala_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('/**', ' * ', ' *', ' */')

    for src in assembly_lang_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == (';', '; ')

    for src in lisp_lang_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == (';;', ';; ')

    for src in erlang_files + prolog_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('%%', '%% ')

    for src in pascal_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('{', ' ', ' ', '}')

    for src in go_and_etc_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('//', '// ')

    for src in script_lang_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('#', '# ')

    for src in coffeescript_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('###', ' ', ' ', '###')

    for src in elm_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('{-', ' ', ' ', '-}')

    for src in ml_lang_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('(*', ' ', ' ', '*)')

    for src in markup_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('<!--', ' ', ' ', '-->')

    for src in vim_script_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('""', '"" ')

    for src in misc_script_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('--', '-- ')

    for src in smalltalk_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('"', ' ', ' ', '"')

def test_license_recognition():
    generator = Generator()

    for lic in licenses():
        generator.set_file_props('file.rb', lic)
        assert generator.rights.spdx_code == lic

def test_file_name_validation():
    invalid_file_names = [
        " ", "\t", " \t ", "\n", " \n", "wrong.", "wrong......", "w`rong.rb",
        "wr<ong.php", "wro>ng.ml", "w:rong.c++", "wron|g.js", "wrong\".ts",
        "'wrong.h", "*wrong.hpp", "wrong-", "wrong--", "wron*g.pl"]
    generator = Generator()

    for fname in invalid_file_names:
        with raises(ValueError):
            generator.set_file_props(fname)
