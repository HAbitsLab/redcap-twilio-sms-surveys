#!/usr/bin/env python

from twilio.rest import Client
from requests import post
import config
from datetime import datetime
import json


class Participant:
    def __init__(self, record_id, phone, current_survey, survey_link):
        self.record_id = record_id
        self.phone = phone
        self.survey_link = survey_link
        self.current_survey = current_survey


# generate participant info
def get_redcap_info():

    fields = "record_id,redcap_event_name,redcap_repeat_instance,redcap_repeat_instrument,phone, " \
             "weekly_survey_complete, " \
             "weekly_survey_2_complete," \
             "weekly_survey_3_complete," \
             "weekly_survey_4_complete," \
             "weekly_survey_5_complete"

    participant_fields = []
    data = {'token': config.redcap_token,
            'format': 'json',
            'content': 'record',  # API call
            'type': 'flat',
            'fields': fields,  # field names specifying specific fields you wish to pull
            'exportSurveyFields': 'true',  # export the survey identifier field
            'forms': 'consent'  # target form
            }

    response = post(config.redcap_api_url, data=data)

    for r_json in response.json():
        # only add participant to collection if they agree and completed consent
        if r_json['agree'] == '1' and r_json['consent_complete'] == '2':
            participant_fields.append(r_json)
    return participant_fields


# Generate SURVEY LINKS
def get_survey_links(record_id, current_survey):
    fields = {
        'token': config.redcap_token,
        'content': 'surveyLink',
        'record': record_id,
        'instrument': current_survey,
        'event': 'event_1_arm_1',
        'format': 'json'
    }

    response = post(config.redcap_api_url, data=fields)

    return response.text


def audit_survey_link(record_id, repeat_instance, redcap_event_name, survey_name):
    now = datetime.now()
    data = {
        'record_id': record_id,
        "message_instance": repeat_instance,
        "last_survey_sent": survey_name,
        "timesent": str(now),
        "sms_log_complete": "2",
        "redcap_event_name": redcap_event_name
    }

    fields = {
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'normal',
        'forceAutoNumber': 'false',
        'token': config.redcap_token,
        'data': json.dumps([data])
    }
    print(data)

    response = post(config.redcap_api_url, data=fields)
    # Check response
    print(response)


def check_for_complete_surveys(redcap_info):
    # check each survey for completion code ('2') on redcap
    if redcap_info['weekly_survey_complete'] != '2':
        return 'weekly_survey'
    elif redcap_info['weekly_survey_2_complete'] != '2':
        return 'weekly_survey_2'
    elif redcap_info['weekly_survey_3_complete'] != '2':
        return 'weekly_survey_3'
    elif redcap_info['weekly_survey_4_complete'] != '2':
        return 'weekly_survey_4'
    elif redcap_info['weekly_survey_5_complete'] != '2':
        return 'weekly_survey_5'
    else:
        return 'Competed'


def send_sms_survey(phone_number, survey_link):
    client = Client(config.twilio_account_sid, config.twilio_token)
    sms_string = "Please complete your weekly survey: {}. Thank you for participating".format(survey_link)
    message = client.messages.create(
         to="+1" + phone_number,
         from_=config.twilio_phone_number,
         body=sms_string)
    # record of message from twilio
    # print(message.sid)

def query_sms_reminders(record_id, current_survey):
    fields = "record_id,redcap_event_name,redcap_repeat_instance,redcap_repeat_instrument"

    participant_fields = []
    data = {'token': config.redcap_token,
            'format': 'json',
            'content': 'record',  # API call
            'type': 'flat',
            'fields': fields,  # field names specifying specific fields you wish to pull
            'exportSurveyFields': 'true',  # export the survey identifier field
            'forms': 'sms_log'  # target form
            }
    response = post(config.redcap_api_url, data=data)

    for r_json in response.json():
        print(r_json)
        if r_json['record_id'] == record_id:
            instance_counter = int(r_json["message_instance"])
            # check if the current sent message is same as last sent message
            # increment survey instance counter
            if r_json["last_survey_sent"] == current_survey:
                instance_counter += 1
            else:
                instance_counter = 1
            return instance_counter


def main():
    try:
        participant_list = []
        redcap_info = get_redcap_info()

        for item in redcap_info:
            survey_name = check_for_complete_surveys(item)

            redcap_event = "texted_" + survey_name

            survey_link = get_survey_links(item['record_id'], survey_name)

            # TODO: use participant object if needed to flag participant for researcher intervention
            part = Participant(item['record_id'], item["phone"],  survey_name, survey_link)
            participant_list.append(part)

            #send_sms_survey(item["phone"], survey_link)
            text_repeats = query_sms_reminders(item['record_id'], survey_name)
            audit_survey_link(item['record_id'], text_repeats, redcap_event, survey_name)

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()

