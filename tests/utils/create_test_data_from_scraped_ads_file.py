import json
import datetime

input_filename = 'ads_20200514_hash_sorted_ssyk0909.json'

file_time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
output_filename = f"reduced_scraped_ads{file_time_stamp}.json"


def reduce_scraped_ads_import_file():
    data = []
    with open(input_filename, 'r', encoding='utf-8') as data_file:
        for item in data_file.readlines():
            data.append(json.loads(item))

    # every 100th ad will be included in output file
    # e.g if input file has 50000 ads, output file will have 500
    new_data = data[0::100]

    with open(output_filename, 'w', encoding='utf-8') as f:
        for dic in new_data:
            tmp = json.dumps(dic, ensure_ascii=False)
            f.write(tmp)
            f.write("\n")


if __name__ == '__main__':
    reduce_scraped_ads_import_file()
