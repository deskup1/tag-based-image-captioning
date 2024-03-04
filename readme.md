
# Tag based image captioning

## Introduction
This is a simple script for generating image captions based on image tags and descriptions.

It uses llm interference to generate tags descriptions and captions.

It work great even with nsfw and nsfl images.

Pleasre, read the whole readme before using this script.

## How it works

In first step (TagProvider), tags descriptions are generated based on wiki from danbooru. It is possible to use different source for tags, but it will require some changes in `tag_provider.py`.

We cannot use wiki tags directly because they are not compact enough and written using markdown syntax.
So we summarizing them in TagProvider using llm and then we use this summary to for additional context when generating captions.

Without providing tag descriptions, captions tends to be garbage.

Tags are cached in `tags_cache.json` folder, so the more tags you generate, the faster it will be.

In second optional step (Interrogator), descriptions are generated using vision model. This step is optional, but it is recommended to use it for better results for images with multiple objects or characters.

For now, this step is working with mixed results but in it should help a little in guiding script in providing better descriptions for different characters or objects in the image.

In third step (Interpreter), captions are generated using instruct model. This step is required for generating captions.

It using tags, tags descriptions and optionally image descriptions to generate captions.

There are 3 template files provided for generating captions:
- interpreter_prompt_template_short.txt - for generating short captions using tags, tags descriptions and image descriptions
- interpreter_prompt_template_short_no_description.txt - for generating short captions using only tags and tags descriptions
- interpreter_prompt_template.txt - for generating long captions using tags, tags descriptions and image descriptions

Feel free to modify them to your needs.
Changing them will have great impact on generated captions.

## Setup
### Install any llm interference software:
For begginers I suggest using [LM Studio](https://lmstudio.ai/)

For advanced usage, you can use [text-generation-webui](https://github.com/oobabooga/text-generation-webui) or [Ollama](https://ollama.com/) or any other llm software you prefer which support OpenAi API.

### Install the required packages:
```bash
pip install -r requirements.txt
```

### Using llm interference of your choosing, download model you will use for creating captions.

I suggest downloading 2 models for better results:
- one instruct model for generating captions and tag descriptions
- one vision model for generating image descriptions

#### Suggested models:
Instruct:
OpenHermes-2.5-Mistral-7B - model finetuded on code but worked surprisingly well for me
Mistral-7B-Instruct-v0.2 - works well for generating captions
Mixtral-8x7B-Instruct-v0.1 - good pick for larger model

For my use case, I used OpenHermes-2.5-Mistral-7B, I didn't need to use higher parameter model

Vision:
llava-v1.6-vicuna-13b - during my testing, using atleast 13b model is required for somewhat decent results
llava-34b-v1.6 - should be good pick but I was unable to test in on my hardware
llava-7b-v1.6 - tends to switch to chinese language for some reason for time to time on lower quantization levels, not recommended
ShareGPT4V-7B - is recommended from my side as 7b model, but you should use higher parameter model if you can

### Prepare your dataset:
Paste your images and tags into `images`.
Tag files should have the same name as the image file (only the extension should be different) and should be in the following format:
```csv
tag1,tag2,tag3
```

### Choose your captioning method:
You can choose between 2 methods of captioning:
- using only instruct model
- vision model for generating descriptions and instruct model for generating tag descriptions and captions

#### Captioning methods:

##### Using only instruct model:
In this mode, captions will be generated based only on image tags, it works great if there is only one object in or character in the image but it can struggle with images containing multiple objects or characters.

- Download the model you will use for generating captions
- Update `config.ini` with your model name and url to your OpenAi API.
- Disable Interrogator in `config.ini` (set `skip` to True)
- Enable TagProvider in `config.ini` (set `skip` to False)
- Enable Interpreter in `config.ini` (set `skip` to False)
- Update Interpreter in `config.ini` to use template 'interpreter_prompt_template_short_no_description.txt' (set `prompt_template_file` to 'interpreter_prompt_template_short_no_description.txt')
- run `caption.py` to generate captions

##### Using vision model for generating descriptions and instruct model for generating tag descriptions and captions:
In this mode, vision model will generate image descriptions and instruct model will generate tag descriptions and captions. This mode works better for images with multiple objects or characters. But it will still struggle with creating decent caption.

It is possible to use vision model for generating captions and tag descriptions, but instruct models will do it better.

- Download the model you will use for generating captions
- Update `config.ini` with your vision model name and url to your OpenAi API.
- Disable Interpreter in `config.ini` (set `skip` to False)
- Enable Interrogator in `config.ini` (set `skip` to True)
- Disable TagProvider in `config.ini` (set `skip` to True)
- run `caption.py` to generate descriptions

- Enable TagProvider in `config.ini` (set `skip` to False)
- Enable Interpreter in `config.ini` (set `skip` to False)
- Update Interpreter in `config.ini` to use template 'interpreter_prompt_template_short.txt' (set `prompt_template_file` to 'interpreter_prompt_template_short.txt')
- run `caption.py` to generate captions


## Results
Results are saved in `captions` folder.

## Additional notes
- Remeber to give large enough context for your model, especially for vision model. Without it, it might crash.
- If you struggle with generating captions for specific subject, add examples of captions in template file to guide your model.
- Start with small amount of images and default settings to see how it works for you (you should only need to change url or port in settings).
- Most amount of time is spent on generating tags descriptions, results are cached in `tags_cache.json`, so the more tags you generate, the faster it will be.

## Requirements
### Minimal requirements
- Python 3.8+
- 6gb of VRAM (you will need to run quantized models)

### Recommended requirements
- Python 3.8+
- 24gb of VRAM (needed for running large vision models)




