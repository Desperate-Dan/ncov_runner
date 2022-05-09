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

    required_group = parser.add_argument_group('Required')
    required_group.add_argument('-b', '--barcodes', dest='input_barcodes', required=True,
                            help='Path to the "barcodes.csv" file for your run')

    optional_group = parser.add_argument_group('Optional')
    optional_group.add_argument('-p', '--prefix', dest='prefix', default="run_number",
                            help='Prefix for the output, Default = RunXXX from barcodes.csv path')
    #optional_group.add_argument('--run', action='store_true', dest='run',
    #                        help='Run ncov-tools after the creation of the config.yaml')
    optional_group.add_argument('--cores', dest='cores', default=8,
                            help='Set number of cores for snakemake to use, Default = 8')
    optional_group.add_argument('--illumina', action='store_true', dest='ill',
                            help='Change config output to work for illumina data')
    optional_group.add_argument('--ref-path', dest='ref_path', default="/data/primer_schemes/nCoV-2019/V4.1/nCoV-2019.reference.fasta",
                            help='Path to SARS-CoV-2 ref')
    optional_group.add_argument('--primer-bed', dest='primer_bed', default="/data/primer_schemes/nCoV-2019/V4.1/nCoV-2019.primer.bed",
                            help='Path to primer bed file')
    optional_group.add_argument('--primer-prefix', dest='primer_prefix', default="SARS-CoV-2",
                            help='Name of the primer prefix WITHIN the primer.bed file, Default = SARS-CoV-2')
    optional_group.add_argument('--output-folder', dest='output_folder', default="ncov-qc",
                            help='Name for folder to send the config.yaml, default = ncov-qc')


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
        return samples_to_exclude

    # write the config.yaml file
    def write_config(input_barcodes, samples_to_exclude, prefix, ref_path, primer_bed, primer_prefix, output_folder):
        config_out_path = os.path.join(os.path.abspath(input_barcodes.rstrip("barcodes.csv")), output_folder)
        try:
            os.mkdir(config_out_path)
        except OSError as error:
            print(error)
            print("Ignore this error, it's just letting you know the ncov-qc folder already exists")
        os.system('chmod 777 %s' % config_out_path)
        new_config = open(config_out_path + "/config.yaml", "w")
        new_config.write("data_root: %s\n\n" % os.path.abspath(input_barcodes.rstrip("barcodes.csv")))
        new_config.write("run_name: %s\n\n" % prefix)
        new_config.write("reference_genome: %s\n\n" % ref_path)
        new_config.write("primer_bed: %s\n\n" % primer_bed)
        if args.ill == True:
            new_config.write("platform: 'illumina' \n\n")
            new_config.write("bam_pattern: '{data_root}/{sample}.mapped.bam' \n\n")
            new_config.write("consensus_pattern: '{data_root}/{sample}.primertrimmed.consensus.fa' \n\n")
            new_config.write("variants_pattern: '{data_root}/{sample}.variants.tsv' \n\n")
        else:
            new_config.write("platform: 'oxford-nanopore' \n\n")
            new_config.write("bam_pattern: '{data_root}/{sample}.sorted.bam' \n\n")
            new_config.write("consensus_pattern: '{data_root}/{sample}.consensus.fasta' \n\n")
            new_config.write("variants_pattern: '{data_root}/{sample}.pass.vcf.gz' \n\n")
        new_config.write("primer_prefix: '%s' \n\n" % primer_prefix)
        new_config.write("negative_control_samples: %s" % str(samples_to_exclude))
        new_config.close()

        return(new_config,config_out_path)

    # run ncov_tools
    #def run_ncov_tools(config_out_path,cores):
    #    print("Starting to ncov-tools pipeline...\n\n")
    #    os.system('cd %s' % config_out_path)
    #    os.system('conda activate ncov-qc')
    #    os.system('snakemake -s /data/COG/ncov-tools/workflow/Snakefile all_qc_reports --cores %s' % cores)
    #    os.system('conda deactivate')


    # This is where the running of the functions lives...
    input_abspath = os.path.abspath(args.input_barcodes)
    samples_to_exclude = get_negatives(input_abspath)
    new_config,config_out_path = write_config(args.input_barcodes, samples_to_exclude, args.prefix, args.ref_path, args.primer_bed, args.primer_prefix, args.output_folder)
    print("\n\nYour config file has been written to '%s'  \n\n" % config_out_path)
    #if args.run == True:
    #    run_ncov_tools(config_out_path,args.cores)

get_arguments()
