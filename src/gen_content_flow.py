# %% [markdown]
# # Functions
from prefect import flow, get_run_logger, task


# %% [markdown]
# ### Gen Niche List

# %%
import pandas as pd
from pytrends.request import TrendReq
# need to modify this to recursivly parse the outputs down the json tree


def gen_niche_list():
    pytrends = TrendReq(hl='en-US')
    json_response = pytrends.categories()
    data = json_response['children']
    prefix = 'metadata_'
    df = pd.json_normalize(
        data, 'children', ['name', 'id'], record_prefix=prefix)
    metadata_cols = [col for col in df.columns if col.startswith(prefix)]
    df = pd.concat(
        [df[['name', 'id']], df[metadata_cols].apply(pd.Series)], axis=1)
    df = df.explode("metadata_children").reset_index(drop=True)
    df = pd.concat([df.drop(["metadata_children"], axis=1),
                   df["metadata_children"].apply(pd.Series)], axis=1)

    # Remove completely NaN columns
    df = df.dropna(axis=1, how='all')

    # Column cleaning operations

    columns = df.columns.tolist()

    # Rename first "name" column to "parent_category"
    columns[0] = 'parent_cat_desc'
    columns[1] = 'parent_cat_id'

    df.columns = columns

    # Column dtype setting

    df['id'] = df['id'].astype('Int64')

    # Explode the final childrens column

    df = df.explode("children").reset_index(drop=True)
    df = pd.concat([df.drop(["children"], axis=1),
                   df["children"].apply(pd.Series)], axis=1)

    # Remove completely NaN columns
    df = df.dropna(axis=1, how='all')

    # Column cleaning operations part 2 lol

    columns_2 = df.columns.tolist()

    # Rename first "name" column to "parent_category"
    columns_2[4] = 'sub_cat_level_1'
    columns_2[5] = 'sub_cat_level_1_id'
    columns_2[6] = 'sub_cat_level_2'
    columns_2[7] = 'sub_cat_level_2_id'

    df.columns = columns_2

    # Explode the final childrens column

    df = df.explode("children").reset_index(drop=True)
    df = pd.concat([df.drop(["children"], axis=1),
                   df["children"].apply(pd.Series)], axis=1)

    # Remove completely NaN columns
    df = df.dropna(axis=1, how='all')

    # Column cleaning operations part 2 lol

    columns_3 = df.columns.tolist()

    # Rename first "name" column to "parent_category"
    columns_3[8] = 'sub_cat_level_3'
    columns_3[9] = 'sub_cat_level_3_id'

    df.columns = columns_3

    df = df.explode("children").reset_index(drop=True)
    df = pd.concat([df.drop(["children"], axis=1),
                   df["children"].apply(pd.Series)], axis=1)

    # Remove completely NaN columns
    df = df.dropna(axis=1, how='all')

    columns_4 = df.columns.tolist()

    # Rename first "name" column to "parent_category"
    columns_4[10] = 'sub_cat_level_4'
    columns_4[11] = 'sub_cat_level_4_id'

    df.columns = columns_4

    df['sub_cat_level_2_id'] = df['sub_cat_level_2_id'].astype('Int64')
    df['sub_cat_level_3_id'] = df['sub_cat_level_3_id'].astype('Int64')
    df['sub_cat_level_4_id'] = df['sub_cat_level_4_id'].astype('Int64')

    df = df.fillna(pd.NA)

    # Define a list of all subcategory columns
    subcategory_columns = ['sub_cat_level_1', 'sub_cat_level_2',
                           'sub_cat_level_3', 'sub_cat_level_4', 'parent_cat_desc']
    subcategory_columns_id = ['sub_cat_level_1_id', 'sub_cat_level_2_id',
                              'sub_cat_level_3_id', 'sub_cat_level_4_id', 'parent_cat_id']

    # Coalesce the subcategory columns into a single column containing only the first non-null value
    df['niche_desc'] = df[subcategory_columns].apply(
        lambda x: x.dropna().iloc[0], axis=1)
    df['niche_id'] = df[subcategory_columns_id].apply(
        lambda x: x.dropna().iloc[0], axis=1)

    df = df.drop(columns=['sub_cat_level_1', 'sub_cat_level_2',
                 'sub_cat_level_3', 'sub_cat_level_4', 'parent_cat_desc'])
    df = df.drop(columns=['sub_cat_level_1_id', 'sub_cat_level_2_id',
                 'sub_cat_level_3_id', 'sub_cat_level_4_id', 'parent_cat_id'])
    df = df.drop(columns=['metadata_name', 'metadata_id'])

    return df


# %%
# could replace top news with top tweets might be better content for the base source to summerize/ mutate


# %% [markdown]
# ### Gen Top News Content

# %%
import pandas as pd
from GoogleNews import GoogleNews
from newspaper import Article, Config, ArticleException


def fetch_top_stories(keyword, n):
    # initialize GoogleNews object
    googlenews = GoogleNews()
    googlenews.set_lang('en')

    # search for top news related to the keyword
    googlenews.search(keyword)

    # get URLs of top n stories
    links = googlenews.get_links()[:n]

    # initialize list to store dataframes
    df_list = []

    # loop through URLs
    for url in links:
        # initialize Article object with custom configuration
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        article = Article(url, config=config)

        try:
            article.download()
            article.parse()

            # check if summary is available
            if article.summary:
                summary = article.summary
            else:
                summary = None

            # create dataframe with metadata and content
            df = pd.DataFrame({
                'title': [article.title],
                'authors': [article.authors],
                'publish_date': [article.publish_date],
                'summary': [summary],
                'content': [article.text],
                'error': [None]
            })

        except ArticleException as e:
            print(f"Article {url} failed with error: {e}")
            # create dataframe with error message
            df = pd.DataFrame({
                'title': [None],
                'authors': [None],
                'publish_date': [None],
                'summary': [None],
                'content': [None],
                'error': [f"Article {url} failed with error: {e}"]
            })

        # add dataframe to list
        df_list.append(df)

    # concatenate dataframes
    result_df = pd.concat(df_list, ignore_index=True)

    return result_df


# %% [markdown]
# ### Build shorts text

# %%
def build_short_text_prompt(title, content):
    """
    Builds a string using the given title and content.
    """
    import re

    # Replace all line breaks, carriage returns, and other non-alphanumeric characters with a space
    cleaned_content = re.sub(r'[\n\r\W]+', ' ', content)

    # Remove any leading or trailing whitespace
    cleaned_content = cleaned_content.strip()

    output_string = f"Find the 3 most interesting fact from the following article and condense them into a bulleted list containing as less than or equal to 9 words each:\n {cleaned_content} \n"

    return output_string


# %%
import openai
import os

openai.api_key = os.environ['open_ai_key']


def generate_interesting_fact(prompt):
    """
    Generates a text completion for the given prompt using the OpenAI API.

    Args:
        prompt (str): The prompt to generate a completion for.

    Returns:
        str: The generated text completion.
    """

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": f"{prompt}"},
    ]
    )

    # Retrieve the generated completion
    response_str = response.choices[0].message.content.strip()

    return response_str


# %% [markdown]
# ### Video & Audio | Download

# %%
# add search block here then download

import requests

# retruns first video id just for demo, could make more advanced search in the future


def get_video_id(resource, api_key, expires, hmac, project_id, user_id, keywords, content_type):

    url = f"https://api.videoblocks.com{resource}?APIKEY={api_key}&EXPIRES={expires}&HMAC={hmac}&project_id={project_id}&user_id={user_id}&keywords={keywords}&content_type={content_type}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return data["results"][0]["id"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


# %%
def fetch_video_url(resource, api_key, expires, hmac, project_id, user_id):

    url = f"https://api.videoblocks.com{resource}?APIKEY={api_key}&EXPIRES={expires}&HMAC={hmac}&project_id={project_id}&user_id={user_id}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return data["MOV"]["_1080p"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


# %%
import os
import requests


def download_video(url, filename):
    # Create the data/video_example directory if it doesn't exist
    os.makedirs('data/video_example', exist_ok=True)

    # Send an HTTP request to the URL
    response = requests.get(url)
    download_path = 'data/video_example/' + filename
    # Open a file for writing in the data/video_example directory
    with open(download_path, 'wb') as f:
        # Write the content of the response to the file
        f.write(response.content)

    return download_path


# %% [markdown]
# ### Audio | download

# %%
# add search block here then download

import requests

# retruns first video id just for demo, could make more advanced search in the future


def get_audio_id(resource, api_key, expires, hmac, project_id, user_id, keywords, content_type):

    url = f"https://api.audioblocks.com{resource}?APIKEY={api_key}&EXPIRES={expires}&HMAC={hmac}&project_id={project_id}&user_id={user_id}&keywords={keywords}&content_type={content_type}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return data["results"][0]["id"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


# %%
def fetch_audio_url(resource, api_key, expires, hmac, project_id, user_id):

    url = f"https://api.audioblocks.com{resource}?APIKEY={api_key}&EXPIRES={expires}&HMAC={hmac}&project_id={project_id}&user_id={user_id}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return data['WAV']
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


# %%
import os
import requests


def download_audio(url, filename):
    # Create the data/video_example directory if it doesn't exist
    os.makedirs('data/video_example', exist_ok=True)

    # Send an HTTP request to the URL
    response = requests.get(url)
    download_path = 'data/video_example/' + filename
    # Open a file for writing in the data/video_example directory
    with open(download_path, 'wb') as f:
        # Write the content of the response to the file
        f.write(response.content)

    return download_path


# %% [markdown]
# ### Video | Composite

# %%
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip

# !cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml
ImageMagickBinary = {
    'magick': '/usr/bin/magick',
    'convert': '/usr/bin/convert'
}


def create_composite(video_path, audio_path, text, font, fontsize, color, pos, output_path):
    # Load the video file
    video_clip = VideoFileClip(video_path)

    # Load the audio file
    audio_clip = AudioFileClip(audio_path)

    # Create the text clip
    text_clip = TextClip(text, fontsize=fontsize, font=font, color=color)

    # setting position of text in the center and duration will be 10 seconds 
    text_clip = text_clip.set_pos('center').set_duration(video_clip.duration)

    audio_clip = audio_clip.set_duration(video_clip.duration)

    # Combine the video clip, audio clip and text clip
    final_clip = CompositeVideoClip([video_clip, text_clip]).set_audio(audio_clip)

    # Write the video clip with the new text overlay and audio to a file
    final_clip.write_videofile(
        filename=output_path,
        audio_codec='aac',
        fps=48,
    )


# %% [markdown]
# # Flow draft

# %%
niche_df = gen_niche_list()
niche_name = niche_df['niche_desc'][0]


top_stories_df = fetch_top_stories(keyword=niche_name, n=5)
title = top_stories_df['title'][0]
content = top_stories_df['content'][0]

# %%
shorts_prompt = build_short_text_prompt(
    title=title,
    content=content
)


# %%
shorts_text_candidate = generate_interesting_fact(
    prompt=shorts_prompt[:1000],
)


# %%
print(shorts_text_candidate)


# %% [markdown]
# ### Execute video grab

# %%
# required modules
import time
import hmac
import hashlib
import os

# Provided by Storyblocks
public_key = os.environ['storyblocks_api_key_public_test']
private_key = os.environ['storyblocks_api_key_private_test']
baseUrl = "https://api.videoblocks.com"
expires = str(int(time.time()))
resource = "/api/v2/videos/search"
hmacBuilder = hmac.new(bytearray(private_key + expires, 'utf-8'),
                       resource.encode('utf-8'), hashlib.sha256)
hmacHex = hmacBuilder.hexdigest()
project_id = "auto_shorts_demo"
user_id = "auto_shorts_bot_process"
keywords = niche_name
content_type = "footage"


video_id = get_video_id(
    resource=resource,
    api_key=public_key,
    expires=expires,
    hmac=hmacHex,
    project_id=project_id,
    user_id=user_id,
    keywords=keywords,
    content_type=content_type,
)


# %%
# required modules
import time
import hmac
import hashlib
import os

# Provided by Storyblocks
public_key = os.environ['storyblocks_api_key_public_test']
private_key = os.environ['storyblocks_api_key_private_test']
baseUrl = "https://api.videoblocks.com"
expires = str(int(time.time()))
resource = f"/api/v2/videos/stock-item/download/{video_id}"
hmacBuilder = hmac.new(bytearray(private_key + expires, 'utf-8'),
                       resource.encode('utf-8'), hashlib.sha256)
hmacHex = hmacBuilder.hexdigest()
project_id = "auto_shorts_demo"
user_id = "auto_shorts_bot_process"


video_url = fetch_video_url(
    resource=resource,
    api_key=public_key,
    expires=expires,
    hmac=hmacHex,
    project_id=project_id,
    user_id=user_id,
)


# %%
niche_clean = niche_name.replace(' ', '_').lower()

video_path = download_video(
    url=video_url,
    filename=f"{niche_clean}_{video_id}.mp4"
)

# %% [markdown]
# ### Find Audio

# %%
# required modules
import time
import hmac
import hashlib
import os

# https://documentation.storyblocks.com/?_ga=2.209332763.846714940.1678072328-561796075.1674608327&_gac=1.252807931.1677039592.CjwKCAiA9NGfBhBvEiwAq5vSy4yIwO38LysWrZvL0h1E3otnsyv6YqT7i4aTe8HTwFTtCfnA08AymxoCTcsQAvD_BwE

# Provided by Storyblocks
public_key = os.environ['storyblocks_api_key_public_test']
private_key = os.environ['storyblocks_api_key_private_test']
baseUrl = "https://api.audioblocks.com"
expires = str(int(time.time()))
resource = "/api/v2/audio/search"
hmacBuilder = hmac.new(bytearray(private_key + expires, 'utf-8'),
                       resource.encode('utf-8'), hashlib.sha256)
hmacHex = hmacBuilder.hexdigest()
project_id = "auto_shorts_demo"
user_id = "auto_shorts_bot_process"
keywords = niche_name
content_type = "music"


audio_id = get_audio_id(
    resource=resource,
    api_key=public_key,
    expires=expires,
    hmac=hmacHex,
    project_id=project_id,
    user_id=user_id,
    keywords=keywords,
    content_type=content_type,
)


# %%
audio_id

# %%
#fetch audio urll

# required modules
import time
import hmac
import hashlib
import os

# Provided by Storyblocks
public_key = os.environ['storyblocks_api_key_public_test']
private_key = os.environ['storyblocks_api_key_private_test']
baseUrl = "https://api.audioblocks.com"
expires = str(int(time.time()))
resource = f"/api/v2/audio/stock-item/download/{audio_id}"
hmacBuilder = hmac.new(bytearray(private_key + expires, 'utf-8'),
                       resource.encode('utf-8'), hashlib.sha256)
hmacHex = hmacBuilder.hexdigest()
project_id = "auto_shorts_demo"
user_id = "auto_shorts_bot_process"


audio_url = fetch_audio_url(
    resource=resource,
    api_key=public_key,
    expires=expires,
    hmac=hmacHex,
    project_id=project_id,
    user_id=user_id,
)


# %%
audio_url

# %%
# need to make the directory this all gets written to temporary and named base don the niche
niche_clean = niche_name.replace(' ', '_').lower()

audio_path = download_audio(
    url=audio_url,
    filename=f"{niche_clean}_{audio_id}.wav"
)


# %% [markdown]
# ### Composite

# %%

@flow
def create_composite(video_path,audio_path,title,shorts_test_candidate) -> None:
    video_path = video_path, 
    audio_path = audio_path,
    text =  f"{title} \n\n {shorts_text_candidate}", 
    font = "DejaVu-Serif-Bold", 
    fontsize = 35, 
    color = "white", 
    pos = None, 
    output_path = 'src/data/video_example/output_edit_example.mp4',

if __name__ == "__main__":
    create_composite()





