import urllib.request
import xml.etree.ElementTree as ET
import json
import sys
import time
import calendar

CHANNELS = {
    "MeetKevin": "UCUvvj5lwue7PspotMDjk5UA",
    "MikeJones": "UCNeBCizpA1NbX7A9_ia6jYg"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds


def get_latest_videos(channel_id, window_hours=2.5):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as response:
                xml_data = response.read().decode("utf-8")

            root = ET.fromstring(xml_data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            yt_ns = {"yt": "http://www.youtube.com/xml/schemas/2015"}

            videos = []
            now = time.time()

            for entry in root.findall("atom:entry", ns):
                video_id = entry.find("yt:videoId", yt_ns).text
                title = entry.find("atom:title", ns).text
                link = entry.find("atom:link", ns).attrib["href"]
                published_str = entry.find("atom:published", ns).text

                # Parse ISO 8601 UTC timestamp correctly using calendar.timegm
                clean_ts = published_str.replace("Z", "").split("+")[0]
                pub_time = calendar.timegm(time.strptime(clean_ts, "%Y-%m-%dT%H:%M:%S"))

                age_hours = (now - pub_time) / 3600
                if age_hours <= window_hours:
                    videos.append({
                        "id": video_id,
                        "title": title,
                        "url": link,
                        "published": published_str,
                    })
            return videos

        except Exception as e:
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    # All retries exhausted — return empty list so agent stays silent,
    # but log the error to stderr for observability.
    print(f"[yt_rss_checker] WARNING: {channel_id} failed after {MAX_RETRIES} attempts: {last_error}", file=sys.stderr)
    return []


if __name__ == "__main__":
    results = {}
    window = float(sys.argv[1]) if len(sys.argv) > 1 else 2.5
    for name, cid in CHANNELS.items():
        results[name] = get_latest_videos(cid, window)
    print(json.dumps(results))
