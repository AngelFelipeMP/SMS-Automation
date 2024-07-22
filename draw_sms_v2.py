from __future__ import print_function
import clicksend_client
from clicksend_client import Contact, ContactList, ContactListApi, ContactApi, SmsCampaignApi, SmsCampaign
from icecream import ic
import os
from API_END_POINTS import AUTH_PATH
import ast
import pandas as pd
from datetime import datetime
import json


class ClickSendSMS:
    def __init__(self, username, password, data_folder_path, participants_file,  winners_file):
        self.username = username
        self.password = password
        self.data_folder_path = data_folder_path
        self.participants_file = participants_file
        self.winners_file =  winners_file
    
    def authorization(self):
        print(f"Checking for Authorization:")
        # Configure HTTP basic authorization: BasicAuth
        self.configuration = clicksend_client.Configuration()
        self.configuration.username = self.username
        self.configuration.password = self.password
        print(f" --> Successful")
    
    def load_data(self):
        print(f"Loading data:")
        self.df_drow_participants = pd.read_csv(f'{self.data_folder_path}/{self.participants_file}.csv')
        self.df_drow_winners = pd.read_csv(f'{self.data_folder_path}/{self.winners_file}.csv')
        print(f" --> Successful")

    def build_sms_text(self):
        print(f"Building SMS text:")
        map_state_acronym= {'New South Wales': 'NSW',
                                'Queensland': 'QLD',
                                'South Australia':'SA',
                                'Western Australia':'WA',
                                'Victoria': 'VIC',}
        
        trail_type = self.participants_file.split('_')[1].split('.')[0]
        info_sms = self.df_drow_winners.loc[self.df_drow_winners['Trial'].str.contains(trail_type), ['Q4.6','Q4.7']].reset_index(drop=True)
        text_sms_beginning = f"Hi from DrivePoints! This week's winner is a driver from {int(info_sms.at[0,'Q4.7'])}, {map_state_acronym[info_sms.at[0,'Q4.6']]}."
        text_sms_ending = f"Enable location access on the app for your chance to win next week."
        self.text_sms = text_sms_beginning + " " + text_sms_ending
        print(f" --> Successful")
        
    def create_contact_list(self):
        print("Creating Contact list:")
        # Create an instance of the ContactListApi API class
        self.contact_list_api = ContactListApi(clicksend_client.ApiClient(self.configuration))

        # Create a new contact list
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_contact_list = ContactList(list_name=f'Contact list {self.current_time}')

        # Send the list throught the contact Api response
        self.contact_list_response = self.contact_list_api.lists_post(new_contact_list)
        print(f" --> Successful")

    def get_id_contact_list(self):
        print("Getting list ID:")
        # Get contact list ID
        contact_list_response_dictionary = ast.literal_eval(self.contact_list_response)
        self.contact_list_id = contact_list_response_dictionary['data']['list_id']
        print(f" --> Successful")

    def add_participants_to_contact_list(self):
        print("Adding participants to contact list:")
        #contact API instance
        contact_api = ContactApi(clicksend_client.ApiClient(self.configuration))
        
        for index, row in self.df_drow_participants.iterrows():
            contact = Contact(phone_number=row['Mobile Number Int'], custom_1=row['Trial'])
            response = contact_api.lists_contacts_by_list_id_post(contact, self.contact_list_id)
        
        print(f" --> {len(self.df_drow_participants)} participants added to contact list")
            
    def create_sms_campaign(self):
        print("Creating SMS campaign:")
        # Now you can use the contact list to send SMS messages
        self.sms_campaign_api = SmsCampaignApi(clicksend_client.ApiClient(self.configuration))

        # Create an SMS campaign
        self.sms_campaign = SmsCampaign(
            name='Weekly Draw ' + self.current_time,
            list_id=self.contact_list_id,
            _from='SafeDrive',
            schedule=0,
            body=self.text_sms)
        print(f" --> Successful")
        
    def send_sms_campaign(self):
        print("Sending SMS campaign:")
        api_response = self.sms_campaign_api.sms_campaigns_send_post(self.sms_campaign)
        print(f" --> Successful")
    
    def main(self):
        self.authorization()
        self.load_data()
        self.build_sms_text()
        self.create_contact_list()
        self.get_id_contact_list()
        self.add_participants_to_contact_list()
        self.create_sms_campaign()
        self.send_sms_campaign()
    
    
if __name__ == '__main__':
    # Load API credentials from JSON file
    with open(AUTH_PATH, 'r') as file:
        auth_dict = json.load(file)
        username = auth_dict['username']
        password = auth_dict['password']
    
    # SEND SMS (feedback, smart, internal)
    for file_name in ['participants_feedback', 'participants_smart', 'participants_internal']:
        winners_file =  'selected_' + ('internals' if 'internal' in file_name else 'participants')
        print(f"###### Group: {file_name}/{winners_file} #######")
        
        # Create an instance of the ClickSendSMS class
        clicksend_sms = ClickSendSMS(username = username, 
                                        password = password,
                                        data_folder_path= os.getcwd() + '/data/users_to_weekly_draw',
                                        participants_file=file_name,
                                        winners_file= winners_file)
        
        clicksend_sms.main()
        print("-----------------------------------------")
