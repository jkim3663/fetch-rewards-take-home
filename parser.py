import argparse
import time
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("file_path", help="Enter a file path to the YAML file")
args = parser.parse_args()

print(args.file_path)