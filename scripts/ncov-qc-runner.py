#!/usr/bin/env python3

# import some bits

import os
import sys
import argparse
import re
import csv


def get_arguments(sysargs = sys.argv[1:]):
    '''
    Parse the command line arguments.
    '''
    parser = argparse.ArgumentParser(description='Makes a config.yaml for your ncov-tools run.')

    main_group = parser.add_argument_group('Main options')
    main_group.add_argument('-b', '--barcodes', dest='input_barcodes', required=True,
                            help='Path to the "barcodes.csv" file for your run')
    main_group.add_argument('-p', '--prefix', dest='prefix', default="run_number",
                            help='Prefix for the output')

    if len(sysargs)<1:
        parser.print_help()
        sys.exit(-1)
    else:
        args = parser.parse_args(sysargs)

    if args.prefix == "run_number":
        input_abspath = os.path.abspath(args.input_barcodes)
        mo = re.search("Run...", input_abspath)
        args.prefix = mo.group(0)

    # define the function for getting negative names
    def get_negatives(input_barcodes):
        samples_to_exclude = []
        with open(input_barcodes, 'r') as input_barcodes:
            read_barcodes = csv.reader(input_barcodes)
            for line in read_barcodes:
                if line[1] == "Negative":
                    samples_to_exclude.append(line[0])
                elif re.search("VTM.*", line[1]):
                    samples_to_exclude.append(line[0])
        print(samples_to_exclude)
        return samples_to_exclude

    input_abspath = os.path.abspath(args.input_barcodes)
    get_negatives(input_abspath)
    print(args.prefix)

get_arguments()
