import requests
import os
import time
import json

# Fill these in with your client_id and client_secret
client_id = 'CLIENT_ID'
client_secret = 'CLIENT_SECRET'
token_storage = 'uber_access_token.json'
seconds_in_day = 86400
ms_in_day = seconds_in_day * 1000


def get_headers(access_token):
    return {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/vnd.mds.provider+json;version=0.3'
    }


def make_request(url, params, headers):
    r = requests.get(url, params=params, headers=headers)
    print(r.url)
    if r.status_code != 200:
        print('Error accessing API' + r.text)
        exit()
    return r.json()


def get_trips(access_token):
    headers = get_headers(access_token)
    max_end_time = int(round(time.time() * 1000)) - ms_in_day
    min_end_time = max_end_time - ms_in_day
    params = {'min_end_time': min_end_time, 'max_end_time': max_end_time}
    return make_request(
        'https://api.uber.com/v0.3/emobility/mds/trips', params, headers)


def get_status_changes(access_token):
    headers = get_headers(access_token)
    end_time = int(round(time.time() * 1000)) - ms_in_day
    start_time = end_time - ms_in_day
    params = {'start_time': start_time, 'end_time': end_time}
    return make_request(
        'https://api.uber.com/v0.3/emobility/mds/status_changes',
        params, headers)


def refresh_token():
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'emobility.mds'
    }

    r = requests.post('https://login.uber.com/oauth/v2/token', data=payload)

    if r.status_code != 200:
        print('Error obtaining access token ' + r.text)
        exit()

    j = r.json()

    expires = time.time() + j['expires_in']
    j['expires_at'] = expires

    with open(token_storage, 'w') as file:
        json.dump(j, file)


def obtain_access_token():
    if not os.path.isfile(token_storage):
        print('Token storage is empty, populating with a new token.')
        refresh_token()

    with open(token_storage, 'r') as f:
        token_response = json.load(f)
        if(token_response['expires_at'] < time.time() - seconds_in_day):
            print('The token is about to expire, refreshing.')
            refresh_token()
            token_response = json.load(f)
        access_token = token_response['access_token']
        print('Using access_token: ' + access_token)
        return access_token


access_token = obtain_access_token()
trips = get_trips(access_token)
device_status = get_status_changes(access_token)

print(json.dumps(trips, indent=2))
print(json.dumps(device_status, indent=2))