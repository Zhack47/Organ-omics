"""Main radiomics extraction script"""

if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    from utils.radiomics import extract_radiomics


    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", type=str, required=True)
    arg_parser.add_argument("-o", type=str, required=True)
    arg_parser.add_argument("--json-file-name", type=str, required=False)

    arguments = arg_parser.parse_args(sys.argv[1:])
    print(arguments.d)
    print(arguments.o)
    print(arguments)
    exit()
    extract_radiomics(arguments.d, arguments.o, arguments.json)
