# -*- coding: utf-8 -*-

"""
Module entry point, when invoked at the command line
"""
import sys
import tempfile
from os import path
from argparse import ArgumentParser, ArgumentError
from cpywrite.generator import Generator, extensions

def main():
    """Prepend a license header to a new or existing source file"""
    parser = ArgumentParser(prog='cpywrite',
                            description="Generate copyright headers for any \
                            open source license")
    parser.add_argument('-v', '--verbatim', action="store_true",
                        dest='verbatim_mode', default=False,
                        help="use full license text as header")
    parser.add_argument('-m', '--machine', action="store_true",
                        dest='cpu_readable', default=False,
                        help="use a machine readable format")
    parser.add_argument('-n', '--noname', action="store_true",
                        dest='no_name', default=False,
                        help="exclude file name from licence header")
    parser.add_argument('-a', '--noanonymous', action="store_true",
                        dest='no_anon', default=False,
                        help="always include the copyright holder's name, even \
                         if the license implies a Public Domain grant")
    parser.add_argument('-l', '--license', action="store", type=str,
                        dest='short_name', default='Apache-2.0',
                        help="SPDX identifier of an open source license \
                         [%(default)s]")
    parser.add_argument('files', nargs='*', metavar='FILES', type=str,
                        help='name(s) of output file(s) (supported extensions: \
                        %s)' % (', '.join(extensions())))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    try:
        args = parser.parse_args()
        filenames = args.files

        if filenames:
            generator = Generator()
            for fnm in map(str.strip, filenames):
                generator.set_file_props(filename=fnm, rights=args.short_name)
                source_file = ''
                license_text = \
                    generator.fetch_license_header(args.verbatim_mode,
                                                   args.cpu_readable,
                                                   args.no_name,
                                                   args.no_anon)
                if license_text:
                    if not path.exists(generator.out_file):
                        with open(generator.out_file, 'w', encoding='utf-8') as src:
                            src.truncate(8)

                        print("Created new %s file: %s"
                              % (generator.lang, generator.out_file))
                    else:
                        with open(generator.out_file + '.bak', 'w', encoding='utf-8') as bak:
                            with open(generator.out_file, 'rt', encoding='utf-8') as source:
                                source_file = source.read()
                                bak.write(source_file)

                    _, tmp_source = tempfile.mkstemp(text=True)

                    with open(tmp_source, 'w', encoding='utf-8') as tmp:
                        tmp.write("%s%s" % (license_text, source_file))

                    with open(tmp_source, 'rt', encoding='utf-8') as new_content:
                        with open(generator.out_file, 'w', encoding='utf-8') as source:
                            source.write(new_content.read())

                else:
                    raise IOError("Error writing file '%s'."
                                  % (generator.out_file))

    except (ArgumentError, UnicodeDecodeError, IOError, AttributeError, ValueError) as exc:
        print(str(exc))
        sys.exit(1)


if __name__ == '__main__':
    main()
