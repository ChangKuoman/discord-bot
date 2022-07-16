import requests

def get_quote():
  response = requests.get("https://zenquotes.io/api/random").json()
  quote = response[0]['q'] + " -" + response[0]['a']
  return quote

def get_cat():
  response = requests.get("https://api.thecatapi.com/v1/images/search").json()
  image_link = response[0]["url"]
  return image_link

def get_dog():
  response = requests.get("https://dog.ceo/api/breeds/image/random").json()
  if response["status"]:
    image_link = response["message"]
    return image_link
  else:
    return "Something went wrong!"
