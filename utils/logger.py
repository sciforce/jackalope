# Copyright 2022 Sciforce Ukraine. All rights reserved.
import logging
import pathlib
import sys

# Create a logger to write to a file
jacka_logger = logging.getLogger('jackalope')
jacka_logger.setLevel(logging.DEBUG)

# Set log format
formatter = logging.Formatter('%(asctime)s: [%(levelname)s] %(name)s - %(message)s')

# Write both to file and to console
handlers = [
        logging.FileHandler(pathlib.Path().cwd() / "jacka.log"),
        logging.StreamHandler(sys.stdout)
        ]

for handler in handlers:
    handler.setFormatter(formatter)
    jacka_logger.addHandler(handler)
