"""Main segmentation script"""

def main():
    import sys
    from os.path import join
    from argparse import ArgumentParser
    from utils.organ_contours import segment_dataset


    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", type=str, required=True)
    arg_parser.add_argument("-o", type=str, required=True)
    arg_parser.add_argument("--json-file-path", type=str, required=True)

    arguments = arg_parser.parse_args(sys.argv[1:])
    segment_dataset(arguments.d, arguments.o, arguments.json_file_path)


if __name__ == "__main__":
    main()
