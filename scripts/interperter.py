import os
import logging
logger = logging.getLogger(__name__)

### class responsible for merging tags and descriptions into caption
class Interpreter:
    def __init__(self, text_generator, **kwargs) -> None:
        self.text_generator = text_generator
        self.target_directory = kwargs["target_directory"]
        self.target_extension = kwargs.get("extension", "caption")
        self.skip = kwargs.get("skip", False)

        # create target directory if it doesn't exist
        if not os.path.exists(self.target_directory):
            os.makedirs(self.target_directory)

        with open(kwargs["prompt_template_file"], "r", encoding='utf-8') as f:
            self.template = f.read()
    
    def get_or_create_caption(self, image: str, tags: str|None, tag_descriptions: str|None, description: str|None) -> str:
        # check if the caption exists
        image_name = os.path.splitext(os.path.basename(image))[0]
        file_path = os.path.join(self.target_directory, image_name + "." + self.target_extension)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read()
            
        if self.skip:
            return ""
        
        if description is None:
            description = ""
        
        if tags is None:
            tags = ""

        if tag_descriptions is None:
            tag_descriptions = ""
            
        # if not, create the caption
        template = self.template.replace("<tags>", tags).replace("<tag_descriptions>", tag_descriptions).replace("<description>", description)
        try:
            logger.info(f"Generating caption for image {image}")
            caption = self.text_generator.generate_text(template).strip().strip("\"")
            logger.debug(caption)

            with open(file_path, "w") as f:
                f.write(caption)

            return caption
        except Exception as e:
            logger.exception(e)
            raise e
        