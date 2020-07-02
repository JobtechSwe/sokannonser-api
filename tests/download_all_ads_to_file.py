import datetime
import json
import requests

api_key = ''
url = "http://127.0.0.1:5000/snapshot"


def download_all_ads():
    response = requests.get(url, headers={'api-key': api_key, 'accept': 'application/json'})
    response.raise_for_status()
    file_time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"all_ads_{file_time_stamp}.py"
    list_of_ads = json.loads(response.content.decode('utf8'))
    with open(file_name, 'a') as out_file:
        out_file.write("all_ads = [\n")  # start of List in file
        for ad in list_of_ads:
            out_file.write(f"{ad},\n")  # write the ad to file, followed by a comma (to make it a List)
        out_file.write("]\n")  # end of List in file


if __name__ == '__main__':
    download_all_ads()
