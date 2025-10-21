"""Main segmentation script"""

if __name__ == "__main__":
    import sys
    from os.path import join
    from argparse import ArgumentParser
    from utils.organ_contours import segment_dataset


    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", type=str)
    arg_parser.add_argument("-o", type=str)
    arg_parser.add_argument("--json-file-name", type=str, required=False, default="dataset.json")

    arguments = arg_parser.parse_args(sys.argv[1:])
    print(f"Contouring images from {join(arguments.d, 'imagesTr')} and putting the results in {join(arguments.o, 'labelsTr')}")
    segment_dataset(arguments.d, arguments.o, arguments.json_file_name)
