import requests
from collections import Counter
import re
from konlpy.tag import Okt

API_KEY = "AIzaSyBZH0RDzhcD__2Ab2TbRfMm9VtNVzVaACE"
VIDEO_URL = "https://www.youtube.com/watch?v=49okHr9jziA"

# 불용어 리스트 (명사/동사/형용사 공통)
STOPWORDS = set([
    "이", "가", "은", "는", "을", "를", "도", "의", "에", "에서", "와", "과", "하고", "보다", "처럼", "같이",
    "하다", "되다", "이다", "있다", "없다", "않다", "같다", "싶다", "보다", "그", "저", "이것", "저것", "그것",
    "수", "것", "등", "및", "제", "저희", "좀", "참", "더", "정말", "진짜", "너무", "완전", "근데", "그래서",
    "그리고", "하지만", "그런데", "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "ㅜㅜ", "ㅋ", "ㅎ", "ㅠ", "ㅜ", "영상", "댓글", "구독", "좋아요"
])

# URL에서 videoId 추출
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu.be/)([\w-]{11})", url)
    return match.group(1) if match else url

def get_comments(video_id, api_key, max_results=50):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": api_key,
        "maxResults": max_results
    }
    response = requests.get(url, params=params)
    data = response.json()
    comments = []
    for item in data.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments

def extract_pos_by_type(comments):
    okt = Okt()
    nouns, verbs, adjectives = [], [], []
    for comment in comments:
        tokens = okt.pos(comment, norm=True, stem=True)
        for word, tag in tokens:
            # 한글/영어만, 불용어 제외, 한 글자 제외
            if not re.match(r"^[가-힣a-zA-Z]+$", word):
                continue
            if word in STOPWORDS or len(word) < 2:
                continue
            if tag == 'Noun':
                nouns.append(word)
            elif tag == 'Verb':
                verbs.append(word)
            elif tag == 'Adjective':
                adjectives.append(word)
    return nouns, verbs, adjectives

def summarize_comments_by_pos(comments):
    nouns, verbs, adjectives = extract_pos_by_type(comments)
    noun_freq = Counter(nouns).most_common(10)
    verb_freq = Counter(verbs).most_common(10)
    adj_freq = Counter(adjectives).most_common(10)
    summary = (
        f"명사 TOP 10: {[n for n, _ in noun_freq]}\n"
        f"동사 TOP 10: {[v for v, _ in verb_freq]}\n"
        f"형용사 TOP 10: {[a for a, _ in adj_freq]}"
    )
    return summary, noun_freq, verb_freq, adj_freq

if __name__ == "__main__":
    video_id = extract_video_id(VIDEO_URL)
    comments = get_comments(video_id, API_KEY)
    summary, noun_freq, verb_freq, adj_freq = summarize_comments_by_pos(comments)
    print("댓글 기반 토픽 분석 결과:")
    print(summary)
    print("\n명사 TOP 10:")
    for word, count in noun_freq:
        print(f"{word}: {count}회")
    print("\n동사 TOP 10:")
    for word, count in verb_freq:
        print(f"{word}: {count}회")
    print("\n형용사 TOP 10:")
    for word, count in adj_freq:
        print(f"{word}: {count}회")
