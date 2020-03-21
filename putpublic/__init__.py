import sys, os
from urllib.parse import urljoin
import requests
import json
import logging
from spinner import Spinner
import pyminizip
import argparse
import string
import random

PP_API = "https://api.putpublic.com"
PP_KEY = "putpublicfreekeyforeveryone"
USAGE = "<STDOUT> | putpublic (optional arguments)"


def random_string(string_length=20):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase + string.digits + string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(string_length))


def utf8len(s):
    return len(s.encode('utf-8'))


# def get_presigned_zip_url():
#     # todo: write function
#     url = urljoin(PP_API, "s3zipurl")
#     return common_presigned_url(url)
#
#
# def get_presigned_url():
#     url = urljoin(PP_API, "s3url")
#     return common_presigned_url(url)


def get_presigned_url(encrypt=False):
    url = urljoin(PP_API, "s3url")
    headers = {"x-api-key": PP_KEY}
    params = {'encrypt': encrypt} if encrypt else {}
    try:
        r = requests.get(url, headers=headers, params=params)
    except requests.exceptions.ConnectionError:
        logging.error(f"Could not connect to {PP_API}, please check your network settings")
        sys.exit(1)
    # print(r.json())
    return r.json()


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
    if http_response.status_code == 204:
        print(f'Uploaded')
        return {"file_url": response['file_url'], "Message": response['Message']}
    else:
        logging.error(f"Could not upload file, message: {http_response.text}")


def upload_zip_to_pp(s):
    response = get_presigned_url(encrypt=True)
    if utf8len(s) > response['max_size']:
        print(f'String size is too big. Max size: {response["max_size"]/(1024*1024)} MB')
        exit(1)

    zip_file, password = create_encrypted_zip_file(s)
    if not zip_file:
        logging.error(f"ZIP file wasn't created")
        return False
    with open(zip_file, "rb") as zip_object:
        files = {'file': zip_object}

        spinner = Spinner()
        print("Uploading...")
        spinner.start()
        try:
            http_response = requests.post(response['url'], data=response['fields'], files=files)
        except requests.exceptions.ConnectionError:
            logging.error(f"Could not connect to {response['url']}, please check your network settings")
            os.remove(zip_file)
            sys.exit(1)
        spinner.stop()

    os.remove(zip_file)

    if http_response.status_code == 204:
        print(f'Uploaded')
        print(f"Zip file password: {password}")
        return {"file_url": response['file_url'], "Message": response['Message']}
    else:
        logging.error(f"Could not upload file, message: {http_response.text}")


def create_encrypted_zip_file(s):
    out_zip_file = os.path.join("./", random_string() + ".zip")
    tmp_text_file = os.path.join("./putpublic_unencrypted_file.txt")
    password = random_string()
    with open(tmp_text_file, 'w') as f:
        f.write(s)
    pyminizip.compress(tmp_text_file, None, out_zip_file, password, 0)
    os.remove(tmp_text_file)
    if os.path.exists(out_zip_file):
        return out_zip_file, password
    else:
        return None, None


def main():
    parser = argparse.ArgumentParser(description="putpublic - makes password protected zip file and upload it to web", usage=USAGE)
    parser.add_argument('-p', action='store_true', default=False, help="upload text without password protecting")
    args = parser.parse_args()

    if not sys.stdin.isatty():
        s = "".join(sys.stdin.readlines())
        if args.p:
            upload_response = upload_to_pp(s)
        else:
            upload_response = upload_zip_to_pp(s)
        if upload_response:
            print(f"{upload_response['Message']}\n{upload_response['file_url']}")
    else:
        print(USAGE)


if __name__ == '__main__':
    main()