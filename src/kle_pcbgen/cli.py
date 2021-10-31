import argparse

from kle_pcbgen import __version__, KLEPCBGenerator


def get_args():
    """Parse the command line and check that the correct number of arguments is given"""
    parser = argparse.ArgumentParser(
        prog="klepcbgen",
        description="Utility to generate a KiCad schematic and layout of the switch matrix of \
a keyboard designed using the Keyboard Layout Editor \
(http://www.keyboard-layout-editor.com/)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--infile",
        required=True,
        help="A JSON file containing a keyboard layout in the KLE JSON format",
    )
    parser.add_argument(
        "--outname",
        required=True,
        help='The base name of the output files (e.g. "id80" will result in "id80.sch" and \
                "id80.pcb"',
    )
    return parser.parse_args()


def main():
    """Main"""
    args = get_args()
    kbpcbgen = KLEPCBGenerator(infile=args.infile, outname=args.outname)
    kbpcbgen.generate_kicadproject()
    kbpcbgen.keyboard.print_key_info()


if __name__ == "__main__":
    main()
