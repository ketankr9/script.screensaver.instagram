import time
import re
import md5
import requests
import json

class HashTag:
    """
    This class helps in extracting image links associated with instagram hashtag, both recent and top posts.
    """
    def __init__(self, tag, tagType="top_posts"):
        """
        tag := the tag you are concerned with scraping
        """
        self.tag = tag
        self.data = None
        self.links = []
        # self.url = ""
        self.tagType = tagType
        self.status = False
        self.scrape()

    def __get_request(self, retry=2):
        url = "https://www.instagram.com/explore/tags/" + self.tag + "/?__a=1"
        
        while not self.status and retry > 0:
            retry-=1
            try:
                r = requests.get(url)
                self.status = True if r.status_code == 200 else False 
                if self.status:
                    return (r.text, True)
            except:
                pass
        
        return ("", False)

    def __clean_data(self, rawData):
        self.data = json.loads(rawData)

    def __extract_tag_links(self, tagType):
        posts = self.data["graphql"]["hashtag"]["edge_hashtag_to_"+self.tagType]["edges"]

        for i in range(len(posts)):
            self.links.append(posts[i]["node"]["display_url"])

    def scrape(self, tagType="top_posts"):
        """
        tagType can take two values:
        top_posts   :=  extract the links of top posts associated with the provided tag
        media       :=  extract the links of most recent posts asscoiated with provided tag
        """
        rawData, status = self.__get_request()
        
        if status:
            self.__clean_data(rawData)
            self.__extract_tag_links(tagType)


class Username:
    """
    This class scrapes the username's timeline pictures.
    username := username to be scrapped
    pCount := number of pages to scrape, where each page has 12 timeline pictures
    """
    def __init__(self, username, pCount=4):
        self.INSTAGRAM_URL = "https://www.instagram.com"
        self.HASHTAG_ENDPOINT = "/graphql/query/?query_hash={}&variables={}"
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        self.pCount = pCount

        self.links = []
        self.status = False
        self.username = username
        self.scrape_username()

    def get_first_page(self):
        r = requests.get(self.INSTAGRAM_URL + "/{}/".format(self.username), headers={"user-agent": self.USER_AGENT})
        json_obj = json.loads(r.text.split("window._sharedData = ")[1].split(";</script>")[0])
        end_cursor = self.get_end_cursor_from_html(r.text)
        edges = json_obj["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
        return (r, [o['node'] for o in edges], end_cursor) 
        
    def get_csrf_token(self,cookies):
        return cookies.get("csrftoken")

    def get_query_id(self,html):
        script_path = re.search(r'/static(.*)ProfilePageContainer\.js/(.*).js', html).group(0)
        script_req = requests.get(self.INSTAGRAM_URL + script_path)
        return re.findall('e\\.profilePosts\\.byUserId\\.get\\(t\\)\\)\\?n\\.pagination:n},queryId:"([^"]*)"', script_req.text)[0]

    def get_user_id(self,html):
        return re.search(r'logging_page_id":"([^"]*)"', html).group(1).split("_")[1]

    def get_rhx_gis(self,html):
        return re.search(r'rhx_gis":"([^"]*)"', html).group(1)

    def get_end_cursor_from_html(self,html):
        return re.search(r'end_cursor":"([^"]*)"', html).group(1)

    def get_end_cursor_from_json(self,json_obj):
        return json_obj['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

    def get_params(self,id, end_cursor):
        return '{{"id":"{}","first":12,"after":"{}"}}'.format(id, end_cursor)

    def get_ig_gis(self,rhx_gis, params):
        return md5.new(rhx_gis + ":" + params).hexdigest()

    def get_posts_from_json(self,json_obj):
        edges = json_obj['data']['user']['edge_owner_to_timeline_media']['edges']
        return [o['node'] for o in edges]

    def make_cookies(self,csrf_token):
        return {
            "csrftoken": csrf_token,
        }

    def make_headers(self,ig_gis):
        return {
            "x-instagram-gis": ig_gis,
            "x-requested-with": "XMLHttpRequest",
            "user-agent": self.USER_AGENT
        }

    def get_next_page(self, csrf_token, ig_gis, query_id, params):
        cookies = self.make_cookies(csrf_token)
        headers = self.make_headers(ig_gis)
        url = self.INSTAGRAM_URL + self.HASHTAG_ENDPOINT.format(query_id, params)
        req = requests.get(url, headers=headers, cookies=cookies)
        req.raise_for_status()
        json_obj = req.json()
        end_cursor = self.get_end_cursor_from_json(json_obj)
        posts = self.get_posts_from_json(json_obj)
        return posts, end_cursor

    def scrape_username(self, sleep=3):
        """
        Yields scraped posts, one by one
        """
        r, posts, end_cursor = self.get_first_page()
        csrf_token = self.get_csrf_token(r.cookies)
        query_id = self.get_query_id(r.text)
        rhx_gis = self.get_rhx_gis(r.text)
        id = self.get_user_id(r.text)
        
        current_page = 0
        for post in posts:
            self.links.append(post['display_url'])
            # yield post
        time.sleep(sleep)

        current_page += 1
        self.status = True
        
        while end_cursor != None and current_page < self.pCount:
            params = self.get_params(id, end_cursor)
            ig_gis = self.get_ig_gis(rhx_gis, params)
            
            posts, end_cursor = self.get_next_page(csrf_token, ig_gis, query_id, params)

            for post in posts:
                self.links.append(post['display_url'])
                # yield post
            current_page +=1
            time.sleep(sleep)


    # def main():
    #     for post in scrape_username():
    #         print post['display_url']
    
