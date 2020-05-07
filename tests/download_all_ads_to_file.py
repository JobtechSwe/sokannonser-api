import sys
import datetime
from sokannonser import app
from tests.integration_tests.test_resources.check_response import check_response_return_json
from sokannonser.settings import NUMBER_OF_ADS, headers


def download_all_ads():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True

    file_time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"all_ads_{file_time_stamp}.py"
    with app.test_client() as testclient:
        limit = 100
        for offset in range(0, NUMBER_OF_ADS, limit):
            result = testclient.get('/search', headers=headers, data={'offset': offset, 'limit': limit})
            json_response = check_response_return_json(result)
            hits = json_response['hits']
            if NUMBER_OF_ADS - offset > limit:
                expected = limit
            else:
                expected = NUMBER_OF_ADS % limit
            assert len(hits) == expected, f"wrong number of hits, actual number: {len(hits)} "
            write_to_file(file_name, hits)


def write_to_file(file_name, ad_list):
    with open(file_name, 'a', encoding="utf-8") as out_file:
        # write some information at the top of the file

        out_file.write("all_ads = [\n")  # start of List in file
        for index, ad in enumerate(ad_list):
            out_file.write(f"{ad},\n")  # write the ad to file, followed by a comma (to make it a List)
            print(index)
        out_file.write("]\n")  # end of List in file


if __name__ == '__main__':
    download_all_ads()
