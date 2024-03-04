from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

class Interrogator:
    def __init__(self, text_generator, **kwargs) -> None:
        self.target_directory = kwargs["target_directory"]
        self.text_generator = text_generator
        self.target_extension = kwargs.get("extension", "description.txt")
        self.skip = kwargs.get("skip", False)

        # create target directory if it doesn't exist
        if not os.path.exists(self.target_directory):
            os.makedirs(self.target_directory)
    
        with open(kwargs["prompt_template_file"], "r", encoding='utf-8') as f:
            self.template = f.read()

    def get_or_create_description(self, image: str) -> str:
        # check if the description exists

        image_name = os.path.splitext(os.path.basename(image))[0]
        file_path = os.path.join(self.target_directory, image_name + "." + self.target_extension)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read()
        
        if self.skip:
            return ""

        try: 
            logger.info(f"Generating description for image {image}")
            description = self.text_generator.generate_multimodal(self.template, image).strip().strip("\"")
            logger.debug(description)
            with open(file_path, "w") as f:
                f.write(description)
            return description

        except Exception as e:
            logger.exception(e)
            raise e