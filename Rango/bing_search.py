import json
import urllib
import codecs
from urllib import parse
from urllib import request
from pprint import pprint


def read_bing_key():
    bing_api_key = None
    try:
        with open('bing.key', encoding='utf-8') as f:
            bing_api_key = f.readline()
    except:
        raise IOError("bing.key file not found.")
    return bing_api_key


def run_query(search_terms):
    bing_api_key = read_bing_key()
    if not bing_api_key:
        raise KeyError("Bing key not found")
    root_url = 'https://api.cognitive.microsoft.com/bing/v5.0/search'
    service = 'webpages'
    count = 10
    offset = 0
    query = parse.quote(search_terms)
    search_url = "{0}?q={1}&responseFilter={2}&count={3}&offset={4}".format(root_url, query,
                                                                            service, count, offset)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; ' \
                 'Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'

    # create request
    bing_request = request.Request(search_url)
    bing_request.add_header('Ocp-Apim-Subscription-Key', bing_api_key)
    bing_request.add_header('User-Agent', user_agent)
    bing_request_opener = request.build_opener()

    # response
    results = []
    response = bing_request_opener.open(bing_request).read()
    response = response.decode('utf-8')
    json_response = json.loads(response)
    for webpage in json_response['webPages']['value']:
        results.append({'title': webpage['name'],
                        'url': webpage['url'],
                        'snippet': webpage['snippet']})

    return results


def main():
    query = input("Enter a query: ")
    results = run_query(query)
    pprint(results)


if __name__ == '__main__':
    main()
