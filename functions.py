import requests
from moviepy.editor import VideoFileClip
from IPython.display import Video
import time
import openai


def generate_response(user_message, OPENAI_API_KEY):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Vous êtes le coach business de l'utilisateur, répondez de manière concise (15 mots) en le tutoyant. Ne dis pas que tu es une intelligence artificielle"},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=100
    )
    return response['choices'][0]['message']['content']

def generate_video(avatar_id, voice_id, input_text, HEYGEN_API_KEY):
    url = "https://api.heygen.com/v2/video/generate"
    headers = {  
        "accept": "application/json",  
        "content-type": "application/json",  
        "x-api-key": HEYGEN_API_KEY,
    }
    data = {
        "video_inputs": [{
            "character": {
                "scale": 1,
                "avatar_id": avatar_id,
                "type": "avatar",
                "avatar_style": "normal"
            },
            "voice": {"type": "text", "input_text": input_text, "voice_id": voice_id},
        }],
        "test": True,
        "caption": True,
        "dimension": {"width": 1080, "height": 1920},
    }
    video_response = requests.post(url, headers=headers, json=data)
    if video_response.status_code == 200:
        response_data = video_response.json()
        video_id = response_data['data'].get('video_id', 'ID non trouvé')
        return video_id
    else:
        print(f"Erreur lors de la génération de la vidéo : {video_response.status_code}")
        return None

def download_video(video_id, HEYGEN_API_KEY, download_path="video_downloaded.mp4", max_retries=5, wait_seconds=70):
    url_status = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    headers = {
        "accept": "application/json",
        "x-api-key": HEYGEN_API_KEY
    }
    for attempt in range(max_retries):
        response_status = requests.get(url_status, headers=headers)
        if response_status.status_code == 200:
            data_status = response_status.json()
            video_url = data_status['data'].get('video_url')
            if video_url:
                response_video = requests.get(video_url)
                if response_video.status_code == 200:
                    with open(download_path, 'wb') as file:
                        file.write(response_video.content)
                    return download_path
                else:
                    print("Échec du téléchargement de la vidéo.")
                    return None
            else:
                time.sleep(wait_seconds)  # Attendre avant de réessayer
        else:
            print("Échec de la récupération des informations de la vidéo.")
            return None
    print("Échec après plusieurs tentatives.")
    return None

def reduce_video_size(input_path, output_path="video_reduced.mp4", resize_factor=0.2):
    try:
        clip = VideoFileClip(input_path)
        clip_resized = clip.resize(resize_factor)
        clip_resized.write_videofile(output_path, verbose=False, logger=None)
    except Exception as e:
        print(f"Erreur lors de la réduction de la vidéo : {e}")