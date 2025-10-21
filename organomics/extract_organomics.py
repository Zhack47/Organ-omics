"""Main radiomics extraction script"""

def main():
    import sys
    from argparse import ArgumentParser
    from utils.radiomics_extraction import extract_radiomics


    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", type=str, required=True)
    arg_parser.add_argument("-o", type=str, required=True)
    arg_parser.add_argument("--json-file-name", type=str, required=False, default="dataset.json")

    arguments = arg_parser.parse_args(sys.argv[1:])
    print(arguments.d)
    print(arguments.o)
    print(arguments)
    extract_radiomics(arguments.d, arguments.o, arguments.json_file_name)


if __name__ == "__main__":
    main()