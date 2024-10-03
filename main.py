"""
Main script.
Create panoramas from a set of images.
"""

import argparse
import logging
import time
from pathlib import Path

import cv2
import numpy as np

from src.images import Image
from src.matching import (
    MultiImageMatches,
    PairMatch,
    build_homographies,
    find_connected_components,
)
from src.rendering import multi_band_blending, set_gain_compensations, simple_blending

print("Libraries imported")
parser = argparse.ArgumentParser(
    description="Create panoramas from a set of images. \
                 All the images must be in the same directory. \
                 Multiple panoramas can be created at once"
)

parser.add_argument(dest="data_dir", type=Path, help="directory containing the images")
parser.add_argument(
    "-mbb",
    "--multi-band-blending",
    action="store_true",
    help="use multi-band blending instead of simple blending",
)
parser.add_argument(
    "--size", type=int, help="maximum dimension to resize the images to"
)
parser.add_argument(
    "--num-bands", type=int, default=5, help="number of bands for multi-band blending"
)
parser.add_argument(
    "--mbb-sigma", type=float, default=1, help="sigma for multi-band blending"
)

parser.add_argument(
    "--gain-sigma-n", type=float, default=10, help="sigma_n for gain compensation"
)
parser.add_argument(
    "--gain-sigma-g", type=float, default=0.1, help="sigma_g for gain compensation"
)

parser.add_argument(
    "-v", "--verbose", action="store_true", help="increase output verbosity"
)

args = vars(parser.parse_args())

if args["verbose"]:
    logging.basicConfig(level=logging.INFO)

logging.info("Gathering images...")

valid_images_extensions = {".jpg", ".png", ".bmp", ".jpeg"}

image_paths = [
    str(filepath)
    for filepath in args["data_dir"].iterdir()
    if filepath.suffix.lower() in valid_images_extensions
]

images = [Image(path, args.get("size")) for path in image_paths]

print("Images Loaded")
print("############################")
logging.info("Found %d images", len(images))
logging.info("Computing features with SIFT...")

i = 1
for image in images:
    image.compute_features()
    print("Features computed: ", i)
    i = i+1
print("############################")


logging.info("Matching images with features...")

matcher = MultiImageMatches(images)
pair_matches: list[PairMatch] = matcher.get_pair_matches()
pair_matches.sort(key=lambda pair_match: len(pair_match.matches), reverse=True)
print("############################")

logging.info("Finding connected components...")

connected_components = find_connected_components(pair_matches)
print("############################")

logging.info("Found %d connected components", len(connected_components))
logging.info("Building homographies...")

build_homographies(connected_components, pair_matches)
print("############################")

time.sleep(0.1)

logging.info("Computing gain compensations...")

i = 1
for connected_component in connected_components:
    component_matches = [
        pair_match
        for pair_match in pair_matches
        if pair_match.image_a in connected_component
    ]

    set_gain_compensations(
        connected_component,
        component_matches,
        sigma_n=args["gain_sigma_n"],
        sigma_g=args["gain_sigma_g"],
    )
    print("Gain Compensation iterations: ", i)
    i = i+1
print("############################")

time.sleep(0.1)

for image in images:
    image.image = (image.image * image.gain[np.newaxis, np.newaxis, :]).astype(np.uint8)

results = []

if args["multi_band_blending"]:
    logging.info("Applying multi-band blending...")
    results = [
        multi_band_blending(
            connected_component,
            num_bands=args["num_bands"],
            sigma=args["mbb_sigma"],
        )
        for connected_component in connected_components
    ]


else:
    logging.info("Applying simple blending...")
    results = [
        simple_blending(connected_component)
        for connected_component in connected_components
    ]
print("############################")

logging.info("Saving results to %s", args["data_dir"] / "results")

home_dir = Path.home()
input_dir_name = args["data_dir"].name
results_path = home_dir / "results" / input_dir_name

logging.info("Saving results to %s", results_path)

print("######################3")
results_path.mkdir(exist_ok=True, parents=True)

print("######################3")
results_path.mkdir(exist_ok=True, parents=True)
for i, result in enumerate(results):
    output_file = results_path / f"pano_{i}.jpg"
    cv2.imwrite(str(output_file), result)
    logging.info("Saved panorama: %s", output_file)
print("Results saved to:", results_path)