from bs4 import BeautifulSoup as BS
import re
from requests import get

def soupify_url(url):
    request = request_url(url)
    return BS(request.text,'html.parser')

def request_url_text(url):
    return request_url(url).text

def request_url(url):
    return get(url, timeout=60.0)

def json_url(url):
    request = request_url(url)
    return request.json()

def soupify_url_retry(url, max_tries = 2):
    count = 0
    soup = None
    while count < max_tries:
        try:
            soup = soupify_url(url)
            break
        except:
            print("error in URL parsing")
            count += 1
    return soup

# All purpose IMDb scraping tool which can fetch the rating and vote counts from archived IMDb pages
# Move to IMDb utilities file
def get_rating_votes(url):
    soup = soupify_url_retry(url)
    if soup:
        span_rating = soup.find_all('span',{'itemprop':'ratingValue'})
        span_votes = soup.find_all('span',{'itemprop':'ratingCount'})
        div_rv = soup.find_all('div','ratingValue')
        re_check = re.findall('[0-9]*\.[0-9]/10[\s\(from]*[0-9\,]{1,}', soup.text)
        digest = [max([len(span_rating), len(span_votes)]), len(div_rv), len(re_check)]

        rating = 0
        votes = 0
        if len(span_rating) == 1 and len(span_votes) == 1:
            rating = float(span_rating[0].text)
            votes = int(span_votes[0].text.replace(',',''))
        elif len(div_rv) == 1:
            rating = float(div_rv[0].find('span').text)
            votes = int(div_rv[0].find_next_sibling('a').text.replace(',',''))
        elif len(re_check) == 1:
            r_string, v_string = re_check[0].split('/10')
            rating = float(r_string)
            votes = int(''.join([a for a in v_string if a.isdigit()]))

        return rating, votes, digest
