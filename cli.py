import os
import sys
import argparse
from utils import dictionary

def cmdline_args():
    args = argparse.ArgumentParser(description='', formatter_class=argparse.RawDescriptionHelpFormatter)

    args.add_argument('-o', '--output_dir', default='output', metavar='', help='Path to the output directory')
    args.add_argument('-in', '--input_path', required=True, metavar='', help='Path to the file csv that contains the name, repo and source')
    # Create a string with all available languages
    available_languages = ', '.join(dictionary.keys())
    language_help = f'Programming language of the input file(s). Available options: {available_languages}'
    args.add_argument('-lang', '--language', nargs='+', default=['python'], metavar='', help=language_help)
    parsed_args = args.parse_args()

    # Check if the input file exists
    if not os.path.isfile(parsed_args.input_path):
        sys.stderr.write(f"The input file does not exist: {parsed_args.input_path}\n")
        sys.exit(1)

    _, file_extension = os.path.splitext(parsed_args.input_path)
    file_extension = file_extension[1:]  # remove the leading dot

    # Check if the file extension is CSV
    if file_extension.lower() != 'csv':
        sys.stderr.write(f"The input file must be a CSV file, but got a .{file_extension} file\n")
        sys.exit(1)

    # Check if the output directory exists, if not create it
    if not os.path.isdir(parsed_args.output_dir):
        os.makedirs(parsed_args.output_dir)

    # Check if the provided language is supported
    for language in parsed_args.language:
        if language not in dictionary.keys():
            sys.stderr.write(f"The provided language is not supported: {language}\n")
            sys.stderr.write("Supported languages are: " + ", ".join(dictionary.keys()) + "\n")
            sys.exit(1)

    return parsed_args

if sys.version_info < (3, 10):
    sys.stderr.write("You need Python 3.10 or later to run this script\n")
    sys.exit(1)

args = cmdline_args()
