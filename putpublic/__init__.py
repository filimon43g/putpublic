import sys
from urllib.parse import urljoin
import requests
import json
import logging
from spinner import Spinner

PP_API = "https://api.putpublic.com"
PP_KEY = "putpublicfreekeyforeveryone"
USAGE = "Usage: <STDOUT> | putpublic"


def utf8len(s):
    return len(s.encode('utf-8'))


def get_presigned_url():
    url = urljoin(PP_API, "s3url")
    headers = {"x-api-key": PP_KEY}
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        logging.error(f"Could not connect to {PP_API}, please check your network settings")
        sys.exit(1)
    return json.loads(r.json()['body'])


def upload_to_pp(tmp_file):
    response = get_presigned_url()
    files = {'file': tmp_file}

    if utf8len(tmp_file) > response['max_size']:
        print(f'String size is too big. Max size: {response["max_size"]/(1024*1024)} MB')
        exit(1)
    spinner = Spinner()
    print("Uploading...")
    spinner.start()
    try:
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    except requests.exceptions.ConnectionError:
        logging.error(f"Could not connect to {response['url']}, please check your network settings")
        sys.exit(1)
    spinner.stop()
    print(f'Uploaded')
    return {"file_url": response['file_url'], "Message": response['Message']}


def main():
    if not sys.stdin.isatty():
        s = "".join(sys.stdin.readlines())
        upload_response = upload_to_pp(s)
        if upload_response:
            print(f"{upload_response['Message']}\n{upload_response['file_url']}")
    else:
        print(USAGE)


if __name__ == '__main__':
    main()