import requests
import logging
import pandas as pd
import tqdm

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

GITHUB_TOKEN = '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'
GITHUB_AUTH_HEADER = {
    'authorization': "token {0}".format(GITHUB_TOKEN),  # Add Github token
}


def search_github(min, max):
    session = requests.Session()

    url = "https://api.github.com/search/repositories?"
    # querystring = {
    #    "q": f"language:python stars:{min}..{max}", "sort": "stars", "per_page": 100}
    querystring = {"q": f"language:python",
                   "sort": "stars forks", "per_page": 100}

    first_page = session.get(url, params=querystring,)  # )
    yield first_page

    next_page = first_page
    while get_next_page(next_page) is not None:
        try:
            next_page_url = next_page.links['next']['url']
            next_page = session.get(
                next_page_url, params=querystring, headers=GITHUB_AUTH_HEADER)
            yield next_page

        except KeyError:
            logging.info("No more Github pages")
            break


def get_next_page(page):
    return page if page.headers.get('link') != None else None


cols = ['owner', 'repo_name', 'url_repo', 'stars',
        'size', 'watchers', 'language', 'has_issues', 'forks', 'open_issues']

df = pd.DataFrame(columns=cols)

# Iterate through pages, parse the results to a dataframe, and stop at 5000 repos.
MIN, MAX = 50, 500

for i in range(5):
    for page in search_github(MIN, MAX):
        try:
            response_dict = page.json()
            # Total repos: 43937
            print("Total repos:", response_dict['total_count'])
            # find total number of repositories
            repos_dicts = response_dict['items']
            print("Repos found:", len(repos_dicts))
            # examine the first repository

            repo_dict = repos_dicts
            for repos_dict in repos_dicts:  # loop through all the dictionaries in repos_dicts.
                # print('Owner:', repos_dict['owner']['login'])
                # print('\nName:', repos_dict['name'])
                # print('Repository:', repos_dict['html_url'])
                # print('Stars:', repos_dict['stargazers_count'])

                # print('Size:', repos_dict['size'])
                # print('Watchers::', repos_dict['watchers_count'])
                # print('Language:', repos_dict['language'])
                # print('Has Issues:', repos_dict['has_issues'])
                # print('Forks:', repos_dict['forks_count'])
                # print('Open Issues:', repos_dict['open_issues_count'])

                df = pd.concat([df, pd.DataFrame(list([[repos_dict['owner']['login'], repos_dict['name'], repos_dict['html_url'], repos_dict['stargazers_count'],
                                                        repos_dict['size'], repos_dict['watchers_count'], repos_dict[
                                                            'language'], repos_dict['has_issues'],
                                                        repos_dict['forks_count'], repos_dict['open_issues_count']]]), columns=cols)])

        except Exception as ex:
            logging.info(
                f"Error!!! parsing gh pages. exception: {str(ex)}")
    MIN += 500
    MAX += 500

df.to_csv('projects_gh.csv')
