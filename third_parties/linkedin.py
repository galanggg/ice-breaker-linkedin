import requests
import os


def scrape_linkedin_profile(linkedin_profile_url: str, mock: bool = False):
    "Scrape information from LinkedIn profile"
    if mock:
        linkedin_profile_url = "https://gist.githubusercontent.com/galanggg/e5dd1ed34a9b25373c77b9ba43b1827d/raw/4da4f696110ddc538c5f677e2cf2136b76643dab/galang_kerta.json"
        response = requests.get(linkedin_profile_url, timeout=5)
    else:
        api_key = os.environ.get("PROXYCURL_API_KEY")
        headers = {"Authorization": "Bearer " + api_key}
        api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
        params = {
            "linkedin_profile_url": linkedin_profile_url,
            "use_cache": "if-present",
            "fallback_to_cache": "on-error",
        }
        response = requests.get(api_endpoint, params=params, headers=headers)
    data = response.json()
    data = {
        k: v
        for k, v in data.items()
        if v not in ([], "", "", None)
        and k not in ["people_also_viewed", "certifications"]
    }
    if data.get("groups"):
        for group_dict in data.get("groups"):
            group_dict.pop("profile_pic_url")
    return data
