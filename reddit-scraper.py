import requests
import time
from collections import Counter
import re

SUBREDDITS = ['news', 'wallstreetbets', 'stocks']
POST_LIMIT = 100

# Stop words to filter out
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
    'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 
    'should', 'may', 'might', 'can', 'about', 'from', 'by', 'as', 'this', 
    'that', 'these', 'those', 'it', 'its', 'they', 'their', 'them', 'we', 
    'our', 'you', 'your', 'he', 'she', 'his', 'her', 'i', 'my', 'me'
}

def fetch_subreddit(subreddit):
    """Fetch posts from a subreddit"""
    url = f'https://www.reddit.com/r/{subreddit}/hot.json?limit={POST_LIMIT}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']['children']
    except Exception as e:
        print(f"Error fetching r/{subreddit}: {e}")
        return []

def extract_keywords(text):
    """Extract keywords from text"""
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    words = text.split()
    
    # Filter out stop words and short words
    return [word for word in words if len(word) > 3 and word not in STOP_WORDS]

def analyze_trends():
    """Main function to analyze Reddit trends"""
    print('🔍 Scraping Reddit...\n')
    
    all_posts = []
    word_freq = Counter()
    
    # Fetch all subreddits
    for sub in SUBREDDITS:
        print(f'Fetching r/{sub}...')
        posts = fetch_subreddit(sub)
        
        for post_data in posts:
            post = post_data['data']
            all_posts.append(post)
            
            # Extract keywords from title
            keywords = extract_keywords(post['title'])
            word_freq.update(keywords)
        
        # Rate limit
        time.sleep(1)
    
    print(f'\n✅ Scraped {len(all_posts)} posts\n')
    
    # Display top trending topics
    print('📊 TOP 20 TRENDING TOPICS:\n')
    for i, (word, count) in enumerate(word_freq.most_common(20), 1):
        print(f'{i}. {word.upper()} ({count} mentions)')
    
    # Display top posts by score
    print('\n🔥 TOP 5 HOTTEST POSTS:\n')
    sorted_posts = sorted(all_posts, key=lambda x: x['score'], reverse=True)
    
    for i, post in enumerate(sorted_posts[:5], 1):
        print(f"{i}. [{post['score']} upvotes] {post['title']}")
        print(f"   r/{post['subreddit']} - https://reddit.com{post['permalink']}\n")

if __name__ == '__main__':
    analyze_trends()