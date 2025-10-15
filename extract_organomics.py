"""Main radiomics extraction script"""

if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    from utils.organomics_extraction import extract_organomics


    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", type=str, required=True)
    arg_parser.add_argument("-o", type=str, required=True)

    arguments = arg_parser.parse_args(sys.argv[1:])
    print(arguments.d)
    print(arguments.o)
    extract_organomics(arguments.d, arguments.o)
