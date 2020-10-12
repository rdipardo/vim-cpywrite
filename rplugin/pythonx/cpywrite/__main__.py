# -*- coding: utf-8 -*-

"""
Module entry point, when invoked at the command line
"""
from __future__ import print_function
import sys
from argparse import ArgumentParser, ArgumentError
from .generator import Generator, extensions

def main():
    """Create a new source file with a license header"""
    parser = ArgumentParser(prog='cpywrite',
                            description="Generate copyright headers for any \
                            open source license")
    parser.add_argument('-v', '--verbatim', action="store_true",
                        dest='verbatim_mode', default=False,
                        help="use full license text as header")
    parser.add_argument('-l', '--license', action="store", type=str,
                        dest='short_name', default='Apache-2.0',
                        help="SPDX identifier of an open source license \
                         (default: %(default)s)")
    parser.add_argument('-n', '--noname', action="store_true",
                        dest='no_name', default=False,
                        help="Exclude file name from licence header")
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
                generator.set_file_props(fnm, args.short_name)
                source_file = \
                    generator.fetch_license_header(args.verbatim_mode,
                                                   args.no_name)
                if source_file:
                    with open(generator.out_file, 'w') as source:
                        source.write(source_file)

                    print("Created new %s file: %s"
                          % (generator.lang, generator.out_file))
                else:
                    raise IOError("Error writing file '%s'."
                                  % (generator.out_file))

    except (ArgumentError, IOError, AttributeError, ValueError) as exc:
        print(str(exc))
        sys.exit(1)


if __name__ == '__main__':
    main()
