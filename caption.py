import scripts.client as Api
from scripts.tag_provider import TagDescriptionProvider
from scripts.interperter import Interpreter
from scripts.interrogator import Interrogator

import tomllib
import logging
import os
import argparse

# set up logging, log to console
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler("caption.log")
                    ])


# load config from file
with open("config.ini", "rb") as f:
    config = tomllib.load(f)

client = Api.OpenAIApiClient(**config["Client"])
tag_provider = TagDescriptionProvider(client, **config["TagProvider"])
interrogator = Interrogator(client, **config["Interrogator"])
interpreter = Interpreter(client, **config["Interpreter"])


parser = argparse.ArgumentParser(description="Generate captions for images")
parser.add_argument("-id", "--image_dir", nargs='?', type=str, help="Directory containing images for which to generate captions", default="images")
parser.add_argument("-td", "--tags_dir", nargs='?', type=str, help="Directory containing tags for the images", default="images")
parser.add_argument("-s", "--supported_image_types", nargs='+', type=str, help="Supported image types", default=["jpg", "jpeg", "png", "gif", "webp"])

args = parser.parse_args()

logger = logging.getLogger(__name__)

image_dir = args.image_dir
if not os.path.exists(image_dir):
    logging.error(f"Image directory not found: {image_dir}")
    exit(1)

tags_dir = args.tags_dir
if not os.path.exists(tags_dir):
    logging.error(f"Tags directory not found: {tags_dir}")
    exit(1)

supported_image_types = args.supported_image_types
# add the dot to the extensions if it's not there
supported_image_types = [f".{ext}" if ext[0] != "." else ext for ext in supported_image_types]


for image in os.listdir(image_dir):

    image_extension = os.path.splitext(image)[1]
    if image_extension not in supported_image_types:
        continue

    logger.info(f"Processing image: {image}")

    image_name = os.path.splitext(image)[0]
    tags_file = os.path.join(tags_dir, image_name + ".txt")
    image_file = os.path.join(image_dir, image)

    # check if the tags file exists
    if not os.path.exists(tags_file):
        logging.warning(f"Tags file not found: {tags_file}")
        continue

    # get the tags
    with open(tags_file, "r") as f:
        tags = f.read()
        tag_descriptions, tags = tag_provider.get_or_create_descriptions_and_tags(tags)

    # get the interrogation
    try:
        description = interrogator.get_or_create_description(image_file)
    except Exception as e:
        logging.exception(e)
        continue

    # get the caption
    try:
        caption = interpreter.get_or_create_caption(image, tags, tag_descriptions, description)
    except Exception as e:
        logging.exception(e)
        continue
    
