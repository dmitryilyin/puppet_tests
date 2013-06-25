import os
import sys


def find_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.pp'):
                file_path = os.path.join(root, file)
                print file_path

find_files(sys.argv[1])