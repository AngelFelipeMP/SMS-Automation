from __future__ import print_function
import clicksend_client
from clicksend_client import Contact, ContactList, ContactListApi, SmsCampaignApi, SmsCampaign, ContactApi
from clicksend_client.rest import ApiException
from icecream import ic
import os
from dotenv import load_dotenv
import ast
import json

# Load environment variables from .env file
load_dotenv()

# Configure HTTP basic authorization: BasicAuth
configuration = clicksend_client.Configuration()
configuration.username = os.environ.get('USERNAME')
configuration.password = os.environ.get('PASSWORD')

try:
    # Create an instance of the API class
    contact_list_api = ContactListApi(clicksend_client.ApiClient(configuration))
    
    # Create a new contact list
    new_contact_list = ContactList(list_name='My Contact List TEST NEW')
    contact_list_response = contact_list_api.lists_post(new_contact_list)
    contact_list_response_dictionary = ast.literal_eval(contact_list_response)
    
    # Get list ID
    contact_list_id = contact_list_response_dictionary['data']['list_id']
    print(f"Contact List ID: {contact_list_id}")

    
    #contact API instance
    contact_api = ContactApi(clicksend_client.ApiClient(configuration))
    
    # Add contacts to the contact list
    contacts = [
        # Contact(first_name='Angel', last_name='Magnossao', phone_number='+61431386743', custom_1='custom_value_1')
        Contact(phone_number='+61431386743', custom_1='custom_value_1')
    ]

    for contact in contacts:
        response = contact_api.lists_contacts_by_list_id_post(contact, contact_list_id)
        # response = contact_list_api.lists_by_list_id_put(contact_list_id, contact)
        print(f"Added contact response: {response}")

    # Fetch the updated contact list to verify
    updated_contact_list = contact_list_api.lists_by_list_id_get(contact_list_id)
    updated_contact_list_dict = ast.literal_eval(updated_contact_list)
    print(f"Updated Contact List: {updated_contact_list_dict}")

    # Now you can use the contact list to send SMS messages
    sms_campaign_api = SmsCampaignApi(clicksend_client.ApiClient(configuration))

    # Create an SMS campaign
    sms_campaign = SmsCampaign(
        name='My SMS Campaign',
        list_id=contact_list_id,
        _from='SafeDrive',
        schedule=0,
        body='Hello, this is a test message!@'
    )

    # Send the SMS campaign
    api_response = sms_campaign_api.sms_campaigns_send_post(sms_campaign)
    ic(api_response)

except ApiException as e:
    print(f"Exception when calling API: {e}")
except Exception as e:
    print(f"General exception: {e}")