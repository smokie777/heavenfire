import pyautogui
import requests
import os
from random import random
from dotenv import load_dotenv; load_dotenv()

filename = 'screenshot.png'
url = 'https://{0}/computervision/imageanalysis:analyze?api-version=2023-02-01-preview&features=denseCaptions'.format(
  os.environ['COMPUTER_VISION_ENDPOINT']
)
headers = {
  'Ocp-Apim-Subscription-Key': os.environ['COMPUTER_VISION_KEY'],
  'Content-Type': 'application/octet-stream'
}

screenshot_react_heavy_immersion_breaking_phrases = ['screen shot', 'shot', 'screen-shot', 'video']
screenshot_react_mild_immersion_breaking_phrases = ['close up of a ', 'close-up of a ', 'blurry image of a ', 'cartoon of a ', 'blurry picture of a',  'blurry image of a']

# takes a screenshot of the main monitor
def take_screenshot():
  screenshot = pyautogui.screenshot()
  screenshot.save(filename)

# DEMO: https://portal.vision.cognitive.azure.com/demo/dense-captioning
# API DOCS: https://centraluseuap.dev.cognitive.microsoft.com/docs/services/unified-vision-apis-public-preview-2023-02-01-preview/operations/61d65934cd35050c20f73ab6
def gen_image_captions():
  with open(filename, 'rb') as f:
    # read file as binary stream and send to Azure API
    data = f.read()

    response = requests.post(
      url=url,
      headers=headers,
      data=data
    )

    json = response.json()

    return json['denseCaptionsResult']['values']

def gen_image_react_prompt(captions, image_type = 'picture'):
  question_prompt = '(ask a question somewhere in the response.) ' if random() < 0.333 else ''
  prompt = 'You\'ve just seen a picture with the following image recognition tags. Give it your best react! Tags: ' if image_type == 'picture' else f'You\'re watching a {image_type} and the current frame has the following image recognition tags. Give it your best react! (Pick only the most interesting one or two tags to react to.) Tags: '

  # clean up any immersion-breaking phrases from azure
  captions_text = [i['text'] for i in captions if not any(
    sub in i['text'] for sub in screenshot_react_heavy_immersion_breaking_phrases
  )]
  for i, s in enumerate(captions_text):
    for sub in screenshot_react_mild_immersion_breaking_phrases:
      captions_text[i] = s.replace(sub, '')

  return f'{question_prompt}{prompt}{", ".join(captions_text)}'


if __name__ == '__main__':
  take_screenshot()
  captions = gen_image_captions()
  print(captions)
  prompt = gen_image_react_prompt(captions, 'picture')
  print(prompt)
  