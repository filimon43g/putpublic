import sys
from urllib.parse import urljoin
import requests
import json
import logging

PP_API = "https://api.putpublic.com"
PP_KEY = "putpublicfreekeyforeveryone"
USAGE = "Usage: <STDOUT> | putpublic"


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
    try:
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    except requests.exceptions.ConnectionError:
        logging.error(f"Could not connect to {response['url']}, please check your network settings")
        sys.exit(1)
    logging.info(f'File upload HTTP status code: {http_response.status_code}')
    return response['file_url']


def main():
    if not sys.stdin.isatty():
        s = "".join(sys.stdin.readlines())
        link = upload_to_pp(s)
        if link:
            print(f"File will be available only one day: {link}")
    else:
        print(USAGE)


if __name__ == '__main__':
    main()