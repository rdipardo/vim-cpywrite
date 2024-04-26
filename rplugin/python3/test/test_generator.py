# -*- coding: utf-8 -*-

from pytest import raises
from cpywrite.generator import Generator, extensions, _get_language_meta
from cpywrite.spdx.license import in_pub_domain, _PD_LICENSE_IDS
from cpywrite import licenses


def test_language_recognition():
    c_lang_files = [
        'file.c', 'file.h', 'file.cc', 'file.CpP', 'file.c++', 'file.CxX',
        'filed.D', 'file.hh', 'file.H++', 'file.hPp', 'file.cs', 'file.CsS',
        'file.java', 'file.KT', 'file.kTs', 'file.Ktm', 'file.M', 'file.mM',
        'file.sWiFt', 'file.VAlA', 'file.vAPi', 'file.cpp2', 'file.h2']
    web_lang_files = [
        'file.JS', 'file.jSx', 'module.MjS', 'file.ts', 'file.pHp',
        'file.phP4', 'file.Php5', 'file.Phtml', 'file.Re', 'file.Rei']
    assembly_lang_files = ['file.S', 'file.s', 'fils.Asm']
    lisp_lang_files = [
        'file.cl', 'file.lSp', 'file.LisP', 'file.cLJ', 'file.CLJC',
        'file.CLjS', 'file.sS', 'file.sCM', 'deps.Edn', 'file.FNl']
    erlang_files = ['file.Erl', 'file.hRl']
    prolog_files = ['file.pRO', 'file.P']
    pascal_files = ['file.PAs', 'file.pP', 'file.iNC', 'pkg.DpK',
        'project.dPr', 'project.LPr']
    scala_files = ['file.sCaLa', 'file.SCala', 'file.sC']
    go_and_etc_files = [
        'file.gO', 'file.Rs', 'file.fs', 'file.fsi', 'file.fsx',
        'file.fsscript', 'file.sCsS']
    script_lang_files = [
        'script', 'script.eX', 'script.ExS', 'script.Sh', 'script.jL',
        'script.pL', 'script.Py', 'script.PyW', 'script.R', 'script.rDA',
        'script.RdAta', 'script.rdS', 'script.Rb', 'script.cMaKe',
        'CMakeLists.tXt', 'Makefile', 'mAKeFIle', 'build.Mk', 'build.mAk',
        'Dockerfile', 'doCKerfILE', 'build.dockerFILE', 'file.YmL', 'file.yAmL',
        'config.PROpertiES', 'Config.properTIEs', 'file.conF', 'file.CoNf']
    dot_files = ['.gitattributes', '.dockerignore', '.xinitrc']
    ini_files = ['config.iNi', 'Config.InI']
    coffeescript_files = ['file.coFFee', 'main.litcoffEe']
    elm_files = ['file.eLm', 'file.Elm', 'file.elM']
    ml_lang_files = ['file.mL', 'file.MlI']
    markup_files = ['file.hTmL', 'file.hTm', 'file.MaRkDoWn', 'file.MD',
                    'file.mKd', 'file.XmL']
    restructuredtext_files = ['file.RsT', 'file.rSt']
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

    for src in assembly_lang_files + ini_files:
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
        assert tokens == ('(*', ' ', ' ', '*)')

    for src in go_and_etc_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('//', '// ')

    for src in script_lang_files + dot_files:
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

    for src in restructuredtext_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('..', '.. ')

    for src in vim_script_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('""', '"" ')

    for src in misc_script_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('--', '-- ')

    for src in smalltalk_files:
        _, _, tokens = _get_language_meta(src)
        assert tokens == ('"', ' ', ' ', '"')

def test_xconfig_recognition():
    ftype, _, tokens = _get_language_meta('.Xresources', 'xdefaults')
    assert ftype == 'Xdefaults'
    assert tokens == ('!', '! ')

def test_license_recognition():
    generator = Generator()

    for lic in licenses():
        generator.set_file_props('file.rb', rights=lic)
        assert generator.rights.spdx_code == lic

def test_public_domain_license_recognition():
    generator = Generator()

    for lic in _PD_LICENSE_IDS:
        generator.set_file_props('file.py', rights=lic)
        assert in_pub_domain(generator.rights.spdx_code)

def test_license_text_generation():
    file_names = [ 'new.py', 'new.php', '.vimrc', 'Makefile' ]
    generator = Generator()

    def generate(verbose=False, tags=False):
        _ = generator.fetch_license_header(
                full_text=verbose,
                cpu_readable=(tags and (not verbose)),
                no_anon=tags)

    for fname in file_names:
        for lic in licenses() + _PD_LICENSE_IDS:
            generator.set_file_props(fname, rights=lic)
            generate()
            generate(verbose=True)
            generate(tags=True)

def test_file_name_validation():
    invalid_file_names = [
        " ", "\t", " \t ", "\n", " \n", "wrong.", "wrong......", "w`rong.rb",
        "wr<ong.php", "wro>ng.ml", "w:rong.c++", "wron|g.js", "wrong\".ts",
        "'wrong.h", "*wrong.hpp", "wrong-", "wrong--", "wron*g.pl"]
    generator = Generator()

    for ext in extensions():
        generator.set_file_props(f'new{ext[1:]}')
        print(repr(generator))
        print(repr(generator.rights))

    for fname in invalid_file_names:
        with raises(ValueError):
            generator.set_file_props(fname)

def test_file_extension_validation():
    with raises(ValueError):
        Generator('new.bad')

def test_license_id_validation():
    with raises(ValueError):
        Generator(rights='¡Licencia-Nada!')
