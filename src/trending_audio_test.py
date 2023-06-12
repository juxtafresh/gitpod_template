# from TikTokApi import TikTokApi
# from moviepy.editor import AudioFileClip

# def get_tiktok_trending_audio(search_term, niche_name_clean, output_len=10):
#     # set up TikTok API client
#     api = TikTokApi()

#     # search for audio clips that match a keyword input
#     results = api.search_music(search_term, count=10)

#     # parse the API response and extract the first result's unique ID
#     if results:
#         music_id = results[0]['id']
#     else:
#         print(f"No results found for keyword '{search_term}'")
#         return None

#     # download the audio clip using its unique ID
#     try:
#         music_data = api.get_music_object(music_id)
#         music_url = music_data['playUrl']
#         music_file = api.get_bytes(music_url)
#     except Exception as e:
#         print(f"Error downloading music: {e}")
#         return None

#     # extract the first output_len seconds of the audio clip
#     music = AudioFileClip(music_file)
#     music_extract = music.subclip(0, output_len)

#     # save the extracted audio clip to disk
#     output_file = f"{niche_name_clean}.mp3"
#     music_extract.write_audiofile(output_file)

#     return output_file

# if __name__ == '__main__':
#     test_path = get_tiktok_trending_audio(
#         search_term='Anime & Manga', 
#         niche_name_clean='anime_&_manga', 
#         output_len=15
#         )

#     print(test_path)


from TikTokApi import TikTokApi
api = TikTokApi()

results = 10

trending = api.trending(count=results)

for tiktok in trending:
    # Prints the id of the tiktok
    print(tiktok['id'])

print(len(trending))