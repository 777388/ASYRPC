import asyncio
import ssl
import re
import json
import multiprocessing
from aiohttp import ClientSession
from xmlrpc.client import ServerProxy
import sys
import urllib
import requests

print("python3 asyrpc.py domain search")
f = open('fil.txt', 'w')
rawr = sys.argv[1]
this = requests.get("http://web.archive.org/cdx/search/cdx?url="+rawr+"&output=text&fl=original&collapse=urlkey&matchType=prefix")
print(this.text, file=f)
f.close()
ef = open('fil.txt', 'r')
urls = []
async def grep_pages(urls, grep_word):
    results = {}
    async with ClientSession() as session:
        tasks = [grep_page(session, url, grep_word) for url in urls]
        for f in asyncio.as_completed(tasks):
            url, data = await f
            if data:
                results[url] = data
    return results


async def grep_page(session, url, grep_word):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                proxy = ServerProxy(url, transport=None, use_datetime=True)
                data = await response.text()
                match = re.search(grep_word, data)
                if match:
                    return url
    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")
def save_results(grep_word, urls):
    try:
        with open(f"{grep_word}.txt", "w") as f:
            json.dump(urls, f)
        print(f"Results saved to {grep_word}.txt")
    except Exception as e:
        print(f"Error occurred while saving results: {e}")

def process_grep(grep_word, urls):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(grep_pages(urls, grep_word))
    save_results(grep_word, results)

if __name__ == "__main__":
    urls = ef.read().splitlines()
    grep_word = str(sys.argv[2])
    p = multiprocessing.Process(target=process_grep, args=(grep_word, urls))
    p.start()
    p.join()
