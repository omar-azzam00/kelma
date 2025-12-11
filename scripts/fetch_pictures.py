import requests as re
import os

SEED = os.urandom(4).hex() 
COUNT = 1000
SAVE_PATH = "./app/static/images/random_pictures"
ABS_PATH = os.path.realpath(SAVE_PATH)

print(f"IMAGES WILL BE SAVED TO: {ABS_PATH}")
print("THE NAMES OF IMAGES WILL BE LIKE profile_001.jpg")
ans = input("DO YOU WANT TO CONTINUE [y/N]? ").strip().lower()
if ans != "y":
    exit(1)
print()
os.makedirs(ABS_PATH, exist_ok=True)

print(f"FETCHING {COUNT} IMAGES WITH SEED {SEED}")
resp = re.get(f"https://randomuser.me/api/?results={COUNT}&seed={SEED}&inc=picture")

if not resp.ok:
    print(resp.status_code)
    print(resp.text)
    exit(1)
json_results = resp.json().get("results")
print()


for i in range(COUNT):
    print(f"IMAGE {i+1}")
    image_url = json_results[i].get("picture").get("large")
    image = re.get(image_url).content
    image_path = ABS_PATH + f"/profile_{i}.jpg"
    f = open(image_path, "wb")
    f.write(image)
    f.close()