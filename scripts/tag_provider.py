import os
import requests
from tinydb import TinyDB, Query
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class TagDescriptionProvider:
    def __init__(self, text_generator, **kwargs) -> None:
        self.text_generator = text_generator
        self.min_post_count = kwargs["min_post_count"]
        self.missing_tags = set()
        self.target_extension = kwargs.get("extension", "txt")
        self.include_tags_without_wiki = kwargs.get("include_tags_without_wiki", False)
        self.skip = kwargs.get("skip", False)

        file_path = kwargs["prompt_template_file"]
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt template file not found: {file_path}")
        
        with open(kwargs["prompt_template_file"], "r", encoding='utf-8') as f:
            self.template = f.read()

        cache_file = kwargs.get("cache_file", "tag_cache.json")
        self.cache = TinyDB(cache_file)

    def get_or_create_description(self, tag: str) -> str:

        # check if the description exists
        if tag in self.missing_tags:
            return None

        # check if the description is already saved 
        tag = tag.strip().replace(" ", "_")
        Tag = Query()
        search_result = self.cache.search(Tag.name == tag)
        if len(search_result) > 0:
            return search_result[0]["description"]
        
        if self.skip:
            return ""
            
        # if not, create the description
        raw_description = self.get_raw_description(tag)
        if raw_description is None:
            self.missing_tags.add(tag)
            self.cache.insert({"name": tag, "description": ""})
            return ""
        
        # save the description to the target directory and return it
        logger.info(f"Generating description for tag {tag}")

        description = self.parse_raw_description(tag, raw_description)
        if description is None:
            self.missing_tags.add(tag)
            self.cache.insert({"name": tag, "description": ""})
            return ""

        logger.debug(description)
        self.cache.insert({"name": tag, "description": description})
        return description
    

    def get_raw_description(self, tag: str) -> str | None:
        tag = tag.strip().replace(" ", "_")
        tags = requests.get("https://danbooru.donmai.us/tags.json?search%5Bname_matches%5D=" + tag)
        if tags.status_code != 200:
            return None

        tags = tags.json()
        if len(tags) == 0:
            logger.warning(f"Tag {tag} not found")
            return None

        tag: dict = tags[0]
        
        if tag.get("post_count") < self.min_post_count:
            logger.warning(f"Tag {tag} has less than {self.min_post_count} posts")
            return None
        
        # get the wiki page
        wiki = requests.get("https://danbooru.donmai.us/wiki_pages/" + str(tag["name"]) + ".json")
        body = wiki.json().get("body")
        if body is None:
            logger.warning(f"Tag {tag} has no wiki page")
            return None
        
        return body
    
    def parse_raw_description(self, tag: str, raw_description: str) -> str:
        tag = tag.strip().replace("_", " ")
        template = self.template.replace("<tag>", tag).replace("<wiki>", raw_description)
        return self.text_generator.generate_text(template)
    
    def get_or_create_descriptions_and_tags(self, tags: str) -> Tuple[str, str]:
        tags = tags.split(",")

        new_tags = []
        descriptions = []
        for tag in tags:
            tag = tag.strip().replace(" ", "_")
            try:
                description = self.get_or_create_description(tag)
                if description:
                    descriptions.append(description)
                    new_tags.append(tag)
                elif self.include_tags_without_wiki:
                    new_tags.append(tag)
            except Exception as e:
                logging.exception(e)
        return "\n".join(descriptions) + "\n", ", ".join(new_tags)