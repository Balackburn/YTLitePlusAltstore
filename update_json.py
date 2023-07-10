import json
import re
import requests

# Fetch the latest release information from GitHub
def fetch_latest_release(repo_url, keyword):
    api_url = f"https://api.github.com/repos/{repo_url}/releases"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(api_url, headers=headers)
    releases = response.json()
    sorted_releases = sorted(releases, key=lambda x: x["published_at"], reverse=True)

    for release in sorted_releases:
        if keyword in release["name"]:
            return release

    raise ValueError(f"No release found containing the keyword '{keyword}'.")

# Update the JSON file with the fetched data
def remove_tags(text):
    text = re.sub('<[^<]+?>', '', text)  # Remove HTML tags
    text = re.sub(r'#{1,6}\s?', '', text)  # Remove markdown header tags
    return text

def update_json_file(json_file, fetched_data):
    with open(json_file, "r") as file:
        data = json.load(file)

    app = data["apps"][0]
    full_version = fetched_data["tag_name"].lstrip('v')
    tag = fetched_data["tag_name"]
    version = re.search(r"(\d+\.\d+\.\d+)", full_version).group(1)
    app["version"] = version
    app["versionDate"] = fetched_data["published_at"]

    description = fetched_data["body"]
    keyword = "YTLitePlus Release Information"
    if keyword in description:
        description = description.split(keyword, 1)[1].strip()

    description = remove_tags(description)
    description = re.sub(r'\*{2}', '', description)
    description = re.sub(r'-', '•', description)
    description = re.sub(r'`', '"', description)

    app["versionDescription"] = description
    app["downloadURL"] = fetched_data["assets"][0]["browser_download_url"]
    app["size"] = fetched_data["assets"][0]["size"]

    # Ensure 'news' key exists in data
    if "news" not in data:
        data["news"] = []

    # Add news entry if there's a new release
    news_identifier = f"release-{full_version}"
    news_entry = {
        "title": f"{full_version}",
        "identifier": news_identifier,
        "caption": f"Version {full_version} of YTLitePlus just got released!",
        "date": fetched_data["published_at"],
        "tintColor": "#000000",
        "imageURL": "https://raw.githubusercontent.com/Balackburn/YTLitePlusAltstore/main/screenshots/news/new_release.png",
        "notify": True,
        "url": f"https://github.com/Balackburn/YTLitePlus/releases/tag/{tag}"
    }

    # Check if the news entry already exists
    news_entry_exists = any(item["identifier"] == news_identifier for item in data["news"])

    # Add the news entry if it doesn't exist
    if not news_entry_exists:
        data["news"].append(news_entry)

    with open(json_file, "w") as file:
        json.dump(data, file, indent=2)
        
# Main function
def main():
    repo_url = "Balackburn/YTLitePlus"
    json_file = "apps.json"
    keyword = "YTLitePlus"

    fetched_data = fetch_latest_release(repo_url, keyword)
    update_json_file(json_file, fetched_data)

if __name__ == "__main__":
    main()