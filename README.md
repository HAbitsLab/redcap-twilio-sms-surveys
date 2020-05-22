# redcap-twilio-sms-surveys
A project to connect REDCap API with Twilio to send sms text messages containing survey links to study participants.

## Overview
This project queries set instruments from a project. The project is set with the REDCap API (each REDCap project has a unique API token). 

1. Queries REDCap the data to see if participants agree to take part in study and consent to survey
2. Associated the phone number with the participant record ID
3. In a collection of surveys defined, finds the completed surveys
4. Generates the survey URL for the next non-completed survey.
5. Sends the Survey URL and simple sms message
6. Logs sms info on REDCap for reference and reminder

- Setting up trials with REDCap and Twilio to test the sms with sample surveys.
- Multiple survey example for use with COVID-19 pandemic 5 week study
- Logging sms information in redcap for use with reminders
- running survey as cron job or Windows scheduled tasks for automation

To run sample the config file needs to be as follows:
```
redcap_token = '##########################'
redcap_api_url = 'https://redcapdemo.vanderbilt.edu/redcap_v9.7.7/API/'
twilio_account_sid = '##########################'
twilio_token = '##########################'
twilio_phone_number = "+1#########"
```
The process for obtaining these keys is described [here](data/README.md)

The redcap url is specific to the institution for production, for the demo REDCap project it is ```https://redcapdemo.vanderbilt.edu/redcap_v9.7.7/API/``` at time of writing (version might be different in future).
