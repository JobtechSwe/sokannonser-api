import requests
import os
from task.slack_tool import SlackMessage, SlackAttachment
from sokannonser import settings

url = {
    'dev': settings.URL_DEV + 'search',
    'stage': settings.URL_STAGE + 'search',
    'prod': settings.URL_PROD + 'search',
}

'q_text_cases.txt'

# channel could be dev, stage, prod


def run_test_cases(file_name, channel1, channel2):
    this_folder = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(this_folder, 'test_cases/' + file_name)

    freetext_hits_result = list()
    freetext_first_hit_result = list()
    freetext_first_ten_hits_result = list()
    with open(my_file, 'r') as file:
        for line in file.readlines():
            q = line.rstrip("\n")
            channel1_result = get_search_result(q, url[channel1])
            channel2_result = get_search_result(q, url[channel2])
            different_count = 0
            sum_count = 0
            sum_count += 1
            # this only use freetext to check hits
            freetext_hits = check_freetext_hits(channel1_result, channel2_result)
            if freetext_hits:
                freetext_hits_result.append(freetext_hits+[q, channel1, channel2])
                different_count += 1

            # this only use freetext to check first hit
            freetext_first_hit = check_freetext_first_hits(channel1_result, channel2_result)
            if freetext_first_hit:
                freetext_first_hit_result.append(freetext_first_hit+[q, channel1, channel2])

            # this is used to check first ten hit is the same or not
            freetext_first_ten_hits = check_freetext_first_ten_hits(channel1_result, channel2_result)
            if freetext_first_ten_hits:
                freetext_first_ten_hits_result.append(freetext_first_ten_hits+[q, channel1, channel2])

    # send slack message
    send_freetext_hits_result_slack_message(freetext_hits_result)
    send_freetext_hit_result_utility_slack_message(different_count, sum_count)
    send_freetext_first_hit_result_slack_message(freetext_first_hit_result)
    send_freetext_first_ten_hits_result_slack_message(freetext_first_ten_hits_result)


def get_search_result(q, env):
    headers = {'api-key': settings.APIKEY, }
    params = {'q': q}

    responses = requests.get(url=env, params=params, headers=headers)
    response_json = responses.json()
    return response_json


color = {
    'red': SlackAttachment.DANGER,
    'yellow': SlackAttachment.WARNING,
    'green': SlackAttachment.GOOD
}


def check_color(different, hits):
    if abs(different) / hits > 0.25:
        return color['red']
    elif abs(different) / hits > 0.01:
        return color['yellow']
    return color['green']


def check_freetext_hits(channel1_result, channel2_result):
    channel1_hits = channel1_result.get('total').get('value')
    channel2_hits = channel2_result.get('total').get('value')
    difference = channel1_hits - channel2_hits
    if difference:
        median = (channel1_hits + channel2_hits) / 2
        colour = check_color(difference, median)
        return [colour, channel1_hits, channel2_hits, difference]
    return difference


def check_freetext_first_hits(channel1_result, channel2_result):
    channel1_hits = channel1_result.get('hits')
    channel2_hits = channel2_result.get('hits')
    channel1_hits_first = channel1_hits[0].get('id', 0) if channel1_hits else 'None'
    channel2_hits_first = channel2_hits[0].get('id', 0) if channel2_hits else 'None'
    different = 0
    if channel1_hits_first != channel2_hits_first:
        different = [channel1_hits_first, channel2_hits_first]
    return different


def check_freetext_first_ten_hits(channel1_result, channel2_result):
    channel1_hits = channel1_result.get('hits')
    channel2_hits = channel2_result.get('hits')

    if len(channel1_hits) >= 10:
        channel1_first_ten = [hit['id'] for hit in channel1_hits[:10]]
    else:
        channel1_first_ten = [hit['id'] for hit in channel1_hits]

    if len(channel2_hits) >= 10:
        channel2_first_ten = [hit['id'] for hit in channel2_hits[:10]]
    else:
        channel2_first_ten = [hit['id'] for hit in channel2_hits]

    different = 0
    if len(channel1_first_ten) != len(channel2_first_ten):
        different = [channel1_first_ten, channel2_first_ten]
    else:
        for i in range(len(channel1_first_ten)):
            if channel1_first_ten[i] != channel2_first_ten[i]:
                different = [channel1_first_ten, channel2_first_ten]
                break
    return different


def send_freetext_hits_result_slack_message(result):
    result = sorted(result, key=lambda item: item[3], reverse=True)
    SlackMessage(channel=settings.TEST_RESULT_CHANNEL,
                 attachments=[SlackAttachment(title="Freetext hits difference",)]).send()

    for colour, channel1_hits, channel2_hits, difference, q, channel1, channel2 in result:
        SlackMessage(
            channel=settings.TEST_RESULT_CHANNEL,
            attachments=[
                SlackAttachment(
                    color=colour,
                    text="{q}: {ch1_h} {ch1} hits & {ch2_h} {ch2} hits: {diff} diff".format(
                        q=q,
                        ch1_h=channel1_hits,
                        ch1=channel1,
                        ch2_h=channel2_hits,
                        ch2=channel2,
                        diff=difference
                    ))
            ]
        ).send()


def send_freetext_hit_result_utility_slack_message(difference, all_count):
    SlackMessage(channel=settings.TEST_RESULT_CHANNEL,
                 attachments=[SlackAttachment(
                     title="Freetext hits difference: {diff}, utility: {utility}%".format(
                         diff=difference,
                         utility=round(difference/all_count*100, 2)
                     ),
                 )]).send()


def send_freetext_first_hit_result_slack_message(result):
    SlackMessage(channel=settings.TEST_RESULT_CHANNEL,
                 attachments=[SlackAttachment(
                     title="Freetext first hit difference",
                 )]).send()

    for channel1_first_hit, channel2_first_hit, q, channel1, channel2 in result:
        SlackMessage(
            channel=settings.TEST_RESULT_CHANNEL,
            attachments=[
                SlackAttachment(
                    color=color['red'],
                    text="{q} first hit: {ch1_hit} {ch1} & {ch2_hit} {ch2}".format(
                        q=q,
                        ch1_hit=channel1_first_hit,
                        ch1=channel1,
                        ch2_hit=channel2_first_hit,
                        ch2=channel2
                    ))
            ]
        ).send()


def send_freetext_first_ten_hits_result_slack_message(result):
    SlackMessage(channel=settings.TEST_RESULT_CHANNEL,
                 attachments=[SlackAttachment(
                     title="Freetext first ten hits difference",
                 )]).send()

    for channel1_first_ten_hit, channel2_first_ten_hit, q, channel1, channel2 in result:
        SlackMessage(
            channel=settings.TEST_RESULT_CHANNEL,
            attachments=[
                SlackAttachment(
                    color=color['red'],
                    text="{q} first 10 hits rank diff: {ch1_hit} {ch1} & {ch2_hit} {ch2}".format(
                        q=q,
                        ch1_hit=str(channel1_first_ten_hit),
                        ch1=channel1,
                        ch2_hit=str(channel2_first_ten_hit),
                        ch2=channel2
                    ))
            ]
        ).send()
