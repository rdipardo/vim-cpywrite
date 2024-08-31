# -*- coding: utf-8 -*-

"""
Utilities for fetching and printing open source license information
"""
import os
import tempfile
import xml.etree.ElementTree as parser
from http import client
from itertools import dropwhile
from re import search, sub
from sys import stderr
from textwrap import TextWrapper
from urllib import request, error as urllib_error
from urllib.parse import quote

__all__ = ['License', 'licenses']


class License():
    """Encapsulates the details of a license on the SPDX index"""
    def __init__(self, code):
        self.spdx_code = None
        self.license_name = None
        self.header_width = 76

        try:
            self.spdx_code = _SPDX_IDS[_SPDX_IDS.index(code)]
        except ValueError as error:
            raise ValueError("No such license '%s' on the SPDX index!"
                             % (code)) from error

    @property
    def header(self):
        """Return the standard header text, if any, of this License"""
        if not self.spdx_code:
            return ''

        # compensate for the deletion of 'Inc.' from the FSF's address:
        # https://github.com/spdx/license-list-XML/commit/fcb4c75#diff-792e39536c2b3cf11dcd8358d7304b1dbb1fea0735c8c8ea98a4882bc6ca8c95
        spdx_revision = 'a7220b6da21b37279659abed0e1b009610931824' \
            if self.spdx_code == 'GPL-2.0-or-later' else 'main'
        xml_resource = 'https://raw.githubusercontent.com/' \
                       'spdx/license-list-XML/%s/src/%s.xml'
        resource = quote(xml_resource % (spdx_revision, self.spdx_code), safe='/:')
        license_data = None
        cache = _find_cached_license(self.spdx_code)
        header_text = []
        should_wrap = False

        if cache:
            try:
                with open(cache, 'r', encoding='utf-8') as tmp:
                    license_data = parser.fromstring(tmp.read())
            except (parser.ParseError, IOError):
                pass

        if license_data is None:
            license_data = _fetch_license(resource, self.spdx_code)

        if license_data is None:
            return ''

        for child in license_data:
            if child.tag == '{http://www.spdx.org/license}license':
                self.license_name = child.attrib.get('name')

        header_tag = \
            './/{http://www.spdx.org/license}standardLicenseHeader'
        p_tag = ('{http://www.spdx.org/license}p')
        alt_tag = ('{http://www.spdx.org/license}alt')
        opt_tag = ('{http://www.spdx.org/license}optional')

        for node in license_data.findall(header_tag):
            for child in node.iter():
                content = ''

                if child.attrib.get('name') == 'copyright':
                    content = child.text
                    if self.spdx_code.startswith('GFDL') and \
                       child.tail:
                        content += child.tail.strip() + ' '
                elif child.attrib.get('name') == 'version':
                    content = child.text
                    if child.tail:
                        content += child.tail or ''
                elif self.spdx_code.startswith('GFDL') and \
                    (child.attrib.get('name') == 'invariantSections' or \
                     child.attrib.get('name') == 'frontCoverTexts' or \
                     child.attrib.get('name') == 'backCoverTexts'):
                    content = child.text
                    if child.tail:
                        content += child.tail.strip() + ' '
                elif child.tag == opt_tag and \
                        child.attrib.get('spacing') == 'after':
                    content = ', ' + child.tail.strip()
                elif self.spdx_code.startswith('GPL-2.0') and child.tag == alt_tag:
                    content = sub(r'\s{2,}', ' ', child.text) + (child.tail or '')
                else:
                    content = child.text if (child.text and \
                                child.tag != alt_tag and \
                                child.tag != opt_tag and \
                                any((ch for ch in child.text if ch.isalpha()))) \
                               else (child.tail or '')

                line = sub(r'\n\s+', '\n', content.lstrip())
                should_wrap = \
                    bool([ln for ln in line.splitlines() \
                          if len(ln) > self.header_width])

                if child.tag == p_tag:
                    header_text.append('\n\n' + line)
                else:
                    header_text.append(line)

        # - drop leading empty lines;
        # - don't break before URLs; but . . .
        # - if a line starts with a URL, indent it;
        # - remove extra space before URLs;
        # - keep authorship on same line as copyright;
        # - remove extra lines between paragraphs
        header = list(
            dropwhile(
                lambda ln: not ln.strip(),
                sub(r'\nhttp',
                    ' http',
                    sub(r'\n{2}http',
                        '\n\n    http',
                        sub(r'(?!\n)\s{2,}http',
                            ' http',
                            sub(r'([cC]opyright(\s+\([cC]\))?)\s*\n',
                                'Copyright (c) ',
                                sub(r'\n{3,}',
                                    '\n\n',
                                    ''.join(header_text)))))).splitlines()))

        return header \
                if not should_wrap \
                else _wrap_header(header, self.header_width)

    @property
    def license_text(self):
        """Return the full text of this License"""
        if not self.spdx_code:
            return ''

        # TODO: find a more reliable license generator: # pylint: disable=W0511
        # https://github.com/spdx/license-list-data/blob/main/text/MIT.txt
        # https://github.com/spdx/license-list-data/blob/main/text/0BSD.txt
        # https://github.com/spdx/license-list-data/blob/2e20899c0504ff6c0acfcc1b0994d7163ce46939/text/Unlicense.txt#L10
        # https://github.com/spdx/license-list-data/blob/2e20899c0504ff6c0acfcc1b0994d7163ce46939/text/BSD-1-Clause.txt#L9
        #
        # full text of new licenses added since v3.11 are fetched from
        # the HEAD of spdx/license-list-data; USE THEM AT YOUR OWN RISK
        spdx_revision = '2e20899c0504ff6c0acfcc1b0994d7163ce46939' \
            if not (self.spdx_code.startswith('CC-BY') or self.spdx_code in [
                'AdaCore-doc',
                'ASWF-Digital-Assets-1.0',
                'ASWF-Digital-Assets-1.1',
                'Boehm-GC',
                'BSD-3-Clause-Modification',
                'BSD-3-Clause-No-Military-License',
                'BSD-4-Clause-Shortened',
                'C-UDA-1.0',
                'DRL-1.0',
                'dtoa',
                'FreeBSD-DOC',
                'GD',
                'Inner-Net-2.0',
                'Latex2e-translated-notice',
                'Linux-man-pages-1-para',
                'Linux-man-pages-copyleft-2-para',
                'Linux-man-pages-copyleft-var',
                'metamail',
                'MIT-Modern-Variant',
                'MIT-Festival',
                'NIST-Software',
                'OGDL-Taiwan-1.0',
                'OLFL-1.3',
                'OPL-UK-3.0',
                'SGP4',
                'TermReadKey',
                'UnixCrypt',
                'Widget-Workshop',
                'Xdebug-1.03',
                'Xfig']) \
            else 'main'

        text_resource = 'https://raw.githubusercontent.com/' \
                       'spdx/license-list-data/' + spdx_revision + \
                       '/text/%s.txt'

        if self.spdx_code in ['Unlicense', 'BSD-1-Clause']:
            text_resource = 'https://raw.githubusercontent.com/' \
                           'spdx/license-list-data/' \
                           'cade284866b0a1b6b18d7cb159279d3d41e6fa07/text/%s.txt'

        resource = quote(text_resource % self.spdx_code, safe='/,:')
        license_text = None
        cache = _find_cached_license(self.spdx_code, '.txt')

        if cache:
            try:
                with open(cache, 'r', encoding='utf-8') as tmp:
                    license_text = tmp.read()
            except IOError:
                pass

        if license_text is None:
            license_text = _fetch_license(resource, self.spdx_code)

        if license_text is None:
            return ''

        # - try to keep sub-clauses left-aligned;
        # - try to preserve indent of copyright notice;
        # - always put copyright notice on a new line;
        # - remove extra lines between paragraphs
        return sub(r'\n{2}\s+\-',
                   '\n\n     -',
                   sub(r'\n{2}\s+[cC]opyright',
                       '\n\n     Copyright',
                       sub(r'(?!$) ([cC]opyright(\s+\([cC]\))?\s+[\<\[\s][yearxYEARX]+)',
                           '\n\nCopyright (c) <year>',
                           sub(r'\n{3,}',
                               '\n\n',
                               license_text)))).splitlines()

    @property
    def tag(self):
        """Return the ID of this License as a machine readable string"""
        return "SPDX-License-Identifier: %s" % self.spdx_code

    def __repr__(self):
        """Return a debug string representing this License"""
        return str((self.__class__.__name__, self.spdx_code))

    def __str__(self):
        """Return the full name of this License"""

        template = "Distributed under the terms of the %s"

        if self.license_name:
            name = self.license_name

            if self.spdx_code.startswith('CC-BY') or in_pub_domain(self.spdx_code):
                return template % name + '.'

            full_name = search(r'[tT]he.+[lL]icense.*$', self.license_name)
            if full_name:
                name = ''.join(full_name.group().split()[1:])

            pretty_name = search(r'.+[lL]icense(.*[vV]ariant)?', name)
            version = search(r'\d\.\d.*$', self.license_name)

            if name:
                return (template % pretty_name.group()) + \
                       (' Version ' + version.group() if version else '') + \
                       '.'

        if self.spdx_code:
            return (template % sub(r'(?!\d)-', ' ', self.spdx_code)) + \
                   (' License.' if not in_pub_domain(self.spdx_code) else '.')

        return ''


def licenses():
    """Return all SPDX ids of candidate licenses"""
    return _SPDX_IDS

def in_pub_domain(license_id):
    """Return True if this License has no copyright requirement"""
    return license_id in _PD_LICENSE_IDS

def _wrap_header(header_lines, limit):
    """Keep header to a prescribed width"""
    wrapper = TextWrapper(drop_whitespace=False, replace_whitespace=False,
                          width=limit)
    header_lines = ['\n' if not s.strip() else s + ' ' for s in header_lines]

    return \
        ''.join(
            '\n'.join([ln.lstrip() for ln \
                       in wrapper.wrap(''.join(header_lines))])).splitlines()

def _find_cached_license(short_name, ext='.xml'):
    """Return the path to a temp file saved with the given SPDX id as prefix"""
    for root, _, files in os.walk(tempfile.gettempdir()):
        found = [f for f in files \
                 if search(r'^(%s)_' % short_name, f) and \
                 os.path.splitext(f)[1] == ext]
        if found:
            return os.path.join(root, found[0])

    return None

def _fetch_license(resource, spdx_id):
    license_data = None
    _, ext = os.path.splitext(resource)

    try:
        with request.urlopen(request.Request(resource)) as response:
            if response.status == 200:
                response_text = response.read().decode('utf8')
                if ext.lower() == '.xml':
                    try:
                        license_data = parser.fromstring(response_text)
                    except (client.IncompleteRead, parser.ParseError, TypeError):
                        print("Got invalid licence data from %s." % (resource),
                              file=stderr)
                else:
                    license_data = response_text

                try:
                    _, temp_file = \
                        tempfile.mkstemp(prefix=spdx_id + '_',
                                         suffix=ext,
                                         text=True)
                    if temp_file:
                        try:
                            with open(temp_file, 'w', encoding='utf-8') as tmp:
                                tmp.write(response_text)
                        except IOError:
                            pass

                except IOError:
                    pass
            else:
                print("Unexpected response [%d] from %s.\n"
                      % (response.status_code, resource),
                      file=stderr)

    except (urllib_error.HTTPError,
            urllib_error.URLError):
        print("Error requesting %s." % (resource), file=stderr)

    return license_data

_SPDX_IDS = [
    '0BSD',
    'AAL',
    'Abstyles',
    'AdaCore-doc',
    'Adobe-2006',
    'Adobe-Glyph',
    'ADSL',
    'AFL-1.1',
    'AFL-1.2',
    'AFL-2.0',
    'AFL-2.1',
    'AFL-3.0',
    'Afmparse',
    'AGPL-1.0-only',
    'AGPL-1.0-or-later',
    'AGPL-3.0-only',
    'AGPL-3.0-or-later',
    'Aladdin',
    'AMDPLPA',
    'AML',
    'AMPAS',
    'ANTLR-PD',
    'ANTLR-PD-fallback',
    'Apache-1.0',
    'Apache-1.1',
    'Apache-2.0',
    'APAFML',
    'APL-1.0',
    'APSL-1.0',
    'APSL-1.1',
    'APSL-1.2',
    'APSL-2.0',
    'Artistic-1.0',
    'Artistic-1.0-cl8',
    'Artistic-1.0-Perl',
    'Artistic-2.0',
    'ASWF-Digital-Assets-1.0',
    'ASWF-Digital-Assets-1.1',
    'Bahyph',
    'Barr',
    'Beerware',
    'BitTorrent-1.0',
    'BitTorrent-1.1',
    'blessing',
    'BlueOak-1.0.0',
    'Boehm-GC',
    'Borceux',
    'BSD-1-Clause',
    'BSD-2-Clause',
    'BSD-2-Clause-Patent',
    'BSD-2-Clause-Views',
    'BSD-3-Clause',
    'BSD-3-Clause-Attribution',
    'BSD-3-Clause-Clear',
    'BSD-3-Clause-LBNL',
    'BSD-3-Clause-Modification',
    'BSD-3-Clause-No-Military-License',
    'BSD-3-Clause-No-Nuclear-License',
    'BSD-3-Clause-No-Nuclear-License-2014',
    'BSD-3-Clause-No-Nuclear-Warranty',
    'BSD-3-Clause-Open-MPI',
    'BSD-4-Clause',
    'BSD-4-Clause-Shortened',
    'BSD-4-Clause-UC',
    'BSD-Protection',
    'BSD-Source-Code',
    'BSL-1.0',
    'BUSL-1.1',
    'bzip2-1.0.5',
    'bzip2-1.0.6',
    'CAL-1.0',
    'CAL-1.0-Combined-Work-Exception',
    'Caldera',
    'CATOSL-1.1',
    'CC0-1.0',
    'CC-BY-1.0',
    'CC-BY-2.0',
    'CC-BY-2.5',
    'CC-BY-2.5-AU',
    'CC-BY-3.0',
    'CC-BY-3.0-AT',
    'CC-BY-3.0-AU',
    'CC-BY-3.0-DE',
    'CC-BY-3.0-IGO',
    'CC-BY-3.0-NL',
    'CC-BY-3.0-US',
    'CC-BY-4.0',
    'CC-BY-NC-1.0',
    'CC-BY-NC-2.0',
    'CC-BY-NC-2.5',
    'CC-BY-NC-3.0',
    'CC-BY-NC-3.0-DE',
    'CC-BY-NC-4.0',
    'CC-BY-NC-ND-1.0',
    'CC-BY-NC-ND-2.0',
    'CC-BY-NC-ND-2.5',
    'CC-BY-NC-ND-3.0',
    'CC-BY-NC-ND-3.0-DE',
    'CC-BY-NC-ND-3.0-IGO',
    'CC-BY-NC-ND-4.0',
    'CC-BY-NC-SA-1.0',
    'CC-BY-NC-SA-2.0',
    'CC-BY-NC-SA-2.0-DE',
    'CC-BY-NC-SA-2.0-FR',
    'CC-BY-NC-SA-2.0-UK',
    'CC-BY-NC-SA-2.5',
    'CC-BY-NC-SA-3.0',
    'CC-BY-NC-SA-3.0-DE',
    'CC-BY-NC-SA-3.0-IGO',
    'CC-BY-NC-SA-4.0',
    'CC-BY-ND-1.0',
    'CC-BY-ND-2.0',
    'CC-BY-ND-2.5',
    'CC-BY-ND-3.0',
    'CC-BY-ND-3.0-DE',
    'CC-BY-ND-4.0',
    'CC-BY-SA-1.0',
    'CC-BY-SA-2.0',
    'CC-BY-SA-2.0-UK',
    'CC-BY-SA-2.1-JP',
    'CC-BY-SA-2.5',
    'CC-BY-SA-3.0',
    'CC-BY-SA-3.0-AT',
    'CC-BY-SA-3.0-DE',
    'CC-BY-SA-3.0-IGO',
    'CC-BY-SA-4.0',
    'CC-PDDC',
    'CDDL-1.0',
    'CDDL-1.1',
    'CDLA-Permissive-1.0',
    'CDLA-Sharing-1.0',
    'CECILL-1.0',
    'CECILL-1.1',
    'CECILL-2.0',
    'CECILL-2.1',
    'CECILL-B',
    'CECILL-C',
    'CERN-OHL-1.1',
    'CERN-OHL-1.2',
    'CERN-OHL-P-2.0',
    'CERN-OHL-S-2.0',
    'CERN-OHL-W-2.0',
    'ClArtistic',
    'CNRI-Jython',
    'CNRI-Python',
    'CNRI-Python-GPL-Compatible',
    'Condor-1.1',
    'copyleft-next-0.3.0',
    'copyleft-next-0.3.1',
    'CPAL-1.0',
    'CPL-1.0',
    'CPOL-1.02',
    'Crossword',
    'CrystalStacker',
    'CUA-OPL-1.0',
    'Cube',
    'C-UDA-1.0',
    'curl',
    'D-FSL-1.0',
    'diffmark',
    'DOC',
    'Dotseqn',
    'DRL-1.0',
    'DSDP',
    'dtoa',
    'dvipdfm',
    'ECL-1.0',
    'ECL-2.0',
    'EFL-1.0',
    'EFL-2.0',
    'eGenix',
    'Entessa',
    'EPICS',
    'EPL-1.0',
    'EPL-2.0',
    'ErlPL-1.1',
    'etalab-2.0',
    'EUDatagrid',
    'EUPL-1.0',
    'EUPL-1.1',
    'EUPL-1.2',
    'Eurosym',
    'Fair',
    'Frameworx-1.0',
    'FreeBSD-DOC',
    'FreeImage',
    'FSFAP',
    'FSFUL',
    'FSFULLR',
    'FTL',
    'GD',
    'GFDL-1.1-invariants-only',
    'GFDL-1.1-invariants-or-later',
    'GFDL-1.1-no-invariants-only',
    'GFDL-1.1-no-invariants-or-later',
    'GFDL-1.1-only',
    'GFDL-1.1-or-later',
    'GFDL-1.2-invariants-only',
    'GFDL-1.2-invariants-or-later',
    'GFDL-1.2-no-invariants-only',
    'GFDL-1.2-no-invariants-or-later',
    'GFDL-1.2-only',
    'GFDL-1.2-or-later',
    'GFDL-1.3-invariants-only',
    'GFDL-1.3-invariants-or-later',
    'GFDL-1.3-no-invariants-only',
    'GFDL-1.3-no-invariants-or-later',
    'GFDL-1.3-only',
    'GFDL-1.3-or-later',
    'Giftware',
    'GL2PS',
    'Glide',
    'Glulxe',
    'gnuplot',
    'GPL-1.0-only',
    'GPL-1.0-or-later',
    'GPL-2.0-only',
    'GPL-2.0-or-later',
    'GPL-3.0-only',
    'GPL-3.0-or-later',
    'gSOAP-1.3b',
    'HaskellReport',
    'Hippocratic-2.1',
    'HPND',
    'HPND-sell-variant',
    'HTMLTIDY',
    'IBM-pibs',
    'ICU',
    'IJG',
    'ImageMagick',
    'iMatix',
    'Imlib2',
    'Info-ZIP',
    'Inner-Net-2.0',
    'Intel',
    'Intel-ACPI',
    'Interbase-1.0',
    'IPA',
    'IPL-1.0',
    'ISC',
    'JasPer-2.0',
    'JPNIC',
    'JSON',
    'LAL-1.2',
    'LAL-1.3',
    'Latex2e',
    'Latex2e-translated-notice',
    'Leptonica',
    'LGPL-2.0-only',
    'LGPL-2.0-or-later',
    'LGPL-2.1-only',
    'LGPL-2.1-or-later',
    'LGPL-3.0-only',
    'LGPL-3.0-or-later',
    'LGPLLR',
    'Libpng',
    'libpng-2.0',
    'libselinux-1.0',
    'libtiff',
    'LiLiQ-P-1.1',
    'LiLiQ-R-1.1',
    'LiLiQ-Rplus-1.1',
    'Linux-man-pages-1-para',
    'Linux-man-pages-copyleft-2-para',
    'Linux-man-pages-copyleft-var',
    'Linux-OpenIB',
    'LPL-1.0',
    'LPL-1.02',
    'LPPL-1.0',
    'LPPL-1.1',
    'LPPL-1.2',
    'LPPL-1.3a',
    'LPPL-1.3c',
    'MakeIndex',
    'metamail',
    'MirOS',
    'MIT',
    'MIT-0',
    'MIT-advertising',
    'MIT-CMU',
    'MIT-enna',
    'MIT-feh',
    'MIT-Festival',
    'MIT-Modern-Variant',
    'MITNFA',
    'MIT-open-group',
    'Motosoto',
    'mpich2',
    'MPL-1.0',
    'MPL-1.1',
    'MPL-2.0',
    'MPL-2.0-no-copyleft-exception',
    'MS-PL',
    'MS-RL',
    'MTLL',
    'MulanPSL-1.0',
    'MulanPSL-2.0',
    'Multics',
    'Mup',
    'NASA-1.3',
    'Naumen',
    'NBPL-1.0',
    'NCGL-UK-2.0',
    'NCSA',
    'NetCDF',
    'Net-SNMP',
    'Newsletr',
    'NGPL',
    'NIST-PD',
    'NIST-PD-fallback',
    'NIST-Software',
    'NLOD-1.0',
    'NLPL',
    'Nokia',
    'NOSL',
    'Noweb',
    'NPL-1.0',
    'NPL-1.1',
    'NPOSL-3.0',
    'NRL',
    'NTP',
    'NTP-0',
    'OCCT-PL',
    'OCLC-2.0',
    'ODbL-1.0',
    'ODC-By-1.0',
    'OFL-1.0',
    'OFL-1.0-no-RFN',
    'OFL-1.0-RFN',
    'OFL-1.1',
    'OFL-1.1-no-RFN',
    'OFL-1.1-RFN',
    'OGC-1.0',
    'OGDL-Taiwan-1.0',
    'OGL-Canada-2.0',
    'OGL-UK-1.0',
    'OGL-UK-2.0',
    'OGL-UK-3.0',
    'OGTSL',
    'OLDAP-1.1',
    'OLDAP-1.2',
    'OLDAP-1.3',
    'OLDAP-1.4',
    'OLDAP-2.0',
    'OLDAP-2.0.1',
    'OLDAP-2.1',
    'OLDAP-2.2',
    'OLDAP-2.2.1',
    'OLDAP-2.2.2',
    'OLDAP-2.3',
    'OLDAP-2.4',
    'OLDAP-2.5',
    'OLDAP-2.6',
    'OLDAP-2.7',
    'OLDAP-2.8',
    'OLFL-1.3',
    'OML',
    'OpenSSL',
    'OPL-1.0',
    'OPL-UK-3.0',
    'OSET-PL-2.1',
    'OSL-1.0',
    'OSL-1.1',
    'OSL-2.0',
    'OSL-2.1',
    'OSL-3.0',
    'O-UDA-1.0',
    'Parity-6.0.0',
    'Parity-7.0.0',
    'PDDL-1.0',
    'PHP-3.0',
    'PHP-3.01',
    'Plexus',
    'PolyForm-Noncommercial-1.0.0',
    'PolyForm-Small-Business-1.0.0',
    'PostgreSQL',
    'PSF-2.0',
    'psfrag',
    'psutils',
    'Python-2.0',
    'Qhull',
    'QPL-1.0',
    'Rdisc',
    'RHeCos-1.1',
    'RPL-1.1',
    'RPL-1.5',
    'RPSL-1.0',
    'RSA-MD',
    'RSCPL',
    'Ruby',
    'Saxpath',
    'SAX-PD',
    'SCEA',
    'Sendmail',
    'Sendmail-8.23',
    'SGI-B-1.0',
    'SGI-B-1.1',
    'SGI-B-2.0',
    'SGP4',
    'SHL-0.5',
    'SHL-0.51',
    'SimPL-2.0',
    'SISSL',
    'SISSL-1.2',
    'Sleepycat',
    'SMLNJ',
    'SMPPL',
    'SNIA',
    'Spencer-86',
    'Spencer-94',
    'Spencer-99',
    'SPL-1.0',
    'SSH-OpenSSH',
    'SSH-short',
    'SSPL-1.0',
    'SugarCRM-1.1.3',
    'SWL',
    'TAPR-OHL-1.0',
    'TCL',
    'TCP-wrappers',
    'TermReadKey',
    'TMate',
    'TORQUE-1.1',
    'TOSL',
    'TU-Berlin-1.0',
    'TU-Berlin-2.0',
    'UCL-1.0',
    'Unicode-DFS-2015',
    'Unicode-DFS-2016',
    'Unicode-TOU',
    'UnixCrypt',
    'Unlicense',
    'UPL-1.0',
    'Vim',
    'VOSTROM',
    'VSL-1.0',
    'W3C',
    'W3C-19980720',
    'W3C-20150513',
    'Watcom-1.0',
    'Widget-Workshop',
    'Wsuipa',
    'WTFPL',
    'X11',
    'Xdebug-1.03',
    'Xerox',
    'Xfig',
    'XFree86-1.1',
    'xinetd',
    'Xnet',
    'xpp',
    'XSkat',
    'YPL-1.0',
    'YPL-1.1',
    'Zed',
    'Zend-2.0',
    'Zimbra-1.3',
    'Zimbra-1.4',
    'Zlib',
    'zlib-acknowledgement',
    'ZPL-1.1',
    'ZPL-2.0',
    'ZPL-2.1']
"""
List of SPDX License Identifiers: https://spdx.org/licenses/
"""

_PD_LICENSE_IDS = [
    'ANTLR-PD', 'ANTLR-PD-fallback', 'CC-PDDC', 'CC0-1.0',
    'libselinux-1.0', 'NIST-PD', 'NIST-PD-fallback', 'PDDL-1.0',
    'SAX-PD', 'SGP4', 'Unlicense']
"""
Licenses with no copyright requirement
"""
