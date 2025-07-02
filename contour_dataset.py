"""Main segmentation script"""

if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    from utils.organ_contours import segment_dataset


    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", type=str)
    arg_parser.add_argument("-o", type=str)

    arguments = arg_parser.parse_args(sys.argv[1:])
    print(arguments.d)
    print(arguments.o)
    segment_dataset(arguments.d, arguments.o)
