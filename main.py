import time
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.leadgenform import LeadgenForm
import requests
import gspread
from google.oauth2 import service_account
import json
from datetime import datetime, timezone
import pytz


# Set up Facebook API connection
def setup_facebook_api(app_id, app_secret, access_token):
  FacebookAdsApi.init(app_id=app_id,
                      app_secret=app_secret,
                      access_token=access_token,
                      api_version='v17.0')


# Set up Google Sheets API connection
def setup_google_sheets_api(credentials_file):
  # scopes = ['https://www.googleapis.com/auth/spreadsheets']
  # credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=scopes)
  # client = gspread.authorize(credentials)
  client = gspread.service_account(filename=credentials_file)
  return client


# Create or update spreadsheet with app name and add leads
def update_spreadsheet(client, spreadsheet_name, sheet_name, leads):
  # Check if the spreadsheet already exists
  spreadsheet = None
  try:
    spreadsheet = client.open(spreadsheet_name)
  except gspread.SpreadsheetNotFound:
    # Create a new spreadsheet
    spreadsheet = client.create(spreadsheet_name)
  sheet = spreadsheet.worksheet(sheet_name)

  # Add app name as the first row
  # app_row = [app_name]
  # sheet.insert_row(app_row, index=1)

  # Add leads to the sheet
  allLeads = []
  for lead in leads:
    print("\n***********\n")
    # adding a timezone
    naive = datetime.now()
    timezone = pytz.timezone("Asia/Kolkata")
    aware1 = timezone.localize(naive)

    # Calling the utcoffset() function
    # over the above localized time
    # print("Time ahead of UTC by:", aware1)
    # print("Time ahead of UTC by:", aware1.utcoffset())
    # print(leads)
    # print("\n***********\n")
    listcheck = [str(aware1), "fb", "", "", "", ""]
    for l in lead['field_data']:
      if (l['name'] == 'name'):
        listcheck[3] = ','.join(l['values'])
      elif (l['name'] == 'phone_number'):
        listcheck[4] = ','.join(l['values'])
        # print("\n***********\n")
        # print(listcheck)
        # print("\n***********\n")
      elif (l['name'] == 'email'):
        listcheck[5] = ','.join(l['values'])
        # print("\n***********\n")
        # print(listcheck)
        # print("\n***********\n")
      else:
        # listcheck[0] = l['name']
        listcheck[2] = ','.join(l['values'])
        # print("\n***********\n")
        # print(listcheck)
        # print("\n***********\n")
        # listcheck.append()
    # print("\n***********\n")
    # print(lead)
    # print("\n***********\n")
    print(listcheck)
    print("\n***********\n")
    allLeads.append(listcheck)
  sheet.append_rows([*allLeads], value_input_option="USER_ENTERED")
  time.sleep(2)


# Main script
def main():
  # Facebook credentials
  fb_app_id = '769678563749973'
  fb_app_secret = '0d7f1a9b04075f8e8de4cc7d826e8c6a'
  fb_access_token = 'EAAK8BMFiMFUBABKvEfkwUDMCoZB0O1Az7lJQmAl7yH0k4LZAMimACZCg5NZBHXMMUnhiwN9ZArI5JSqa3aZCXHmxNX5VF4htrZAZCiJAZCa6mBclcn9bffZBv9QXZBbPfLGN9N1GwhaKnZATIeuUFCn6Pq1DWZCh5KNdZBUrTPFX3vEGfo4DKfmH7bmSTq'
  graph = setup_facebook_api(fb_app_id, fb_app_secret, fb_access_token)

  # Google Sheets credentials
  google_credentials_file = 'youtech_goole_credantials.json'
  client = setup_google_sheets_api(google_credentials_file)

  # Campaign ID
  # campaign_id = '23853497642620620'
  spreadsheet_name = "KGIF Institute Leads Feedback"
  campaign_list = [
    {
      "campaign_id": '23855028975300471',
      "spreadsheet_name": 'Kolhapur - Automated Sheet',
      "leads": []
    },
    {
      "campaign_id": '23854804044890471',
      "spreadsheet_name": 'MBBS  INDIA - Automated Sheet',
      "leads": []
    },
  ]

  while True:
    for campaign in campaign_list:
      # Retrieve ads from Facebook campaign
      url = f'https://graph.facebook.com/v17.0/{campaign["campaign_id"]}/ads'
      params = {
        'access_token': fb_access_token,
        'fields': 'id'
        # 'limit': 10  # Adjust the limit based on your requirements
      }

      response = requests.get(url, params=params)
      data = response.json()
      print(data)
      ads = data['data']
      print(len(ads))

      # Fetch leads from each ad
      leads = []
      for ad in ads:
        ad_id = ad['id']
        url = f'https://graph.facebook.com/v17.0/{ad_id}/leads'
        params = {
          'access_token': fb_access_token,
          'fields': 'field_data'
          # 'limit': 10  # Adjust the limit based on your requirements
        }

        response = requests.get(url, params=params)
        data = response.json()
        # print(data)
        leads.extend(data['data'])

        while 'paging' in data and 'next' in data['paging']:
          response = requests.get(data['paging']['next'])
          data = response.json()
          leads.extend(data['data'])

      # Update or create spreadsheet and add leads
      # time.sleep(5)
      # Convert dictionaries to tuples of key-value pairs
      different_objects = []
      # Iterate over objects in list2
      for obj2 in leads:
        if obj2 not in campaign["leads"]:
          different_objects.append(obj2)

      # print(json.dumps(different_objects))
      if (len(different_objects) == 0):
        print(len(different_objects))
        print("same")
      else:
        print(len(different_objects))
        campaign["leads"] = leads
        print("not same")
        update_spreadsheet(client, spreadsheet_name,
                           campaign["spreadsheet_name"], different_objects)
        time.sleep(60)
      #   campaign["leads"] = leads
      #   print(len(leads))
      # print(len(campaign["leads"]))

      # # Wait for a minute before the next update


if __name__ == '__main__':
  main()
