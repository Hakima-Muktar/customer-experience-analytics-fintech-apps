"""
Configuration file for Bank Reviews Analysis Project
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Play Store App IDs (3 banks as per challenge requirements)
APP_IDS = {
    'CBE': os.getenv('CBE_APP_ID', 'com.combanketh.mobilebanking'),
    'BOA': os.getenv('BOA_APP_ID', 'com.boa.boaMobileBanking'),
    'Dashen': os.getenv('DASHEN_APP_ID', 'com.dashen.dashensuperapp'),
}

# Bank Names Mapping
BANK_NAMES = {
    'CBE': 'Commercial Bank of Ethiopia',
    'BOA': 'Bank of Abyssinia',
    'Dashen': 'Dashen Bank',
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'reviews_per_bank': int(os.getenv('REVIEWS_PER_BANK', 1500)),
    'max_retries': int(os.getenv('MAX_RETRIES', 3)),
    'lang': 'en',
    'country': 'et'  # Ethiopia
}

# File Paths
DATA_PATHS = {
    'raw': 'data/raw',
    'processed': 'data/processed',
    'raw_reviews': 'data/raw/reviews_raw.csv',
    'processed_reviews': 'data/processed/reviews_processed.csv',
    'sentiment_results': 'data/processed/reviews_with_sentiment.csv',
    'final_results': 'data/processed/reviews_final.csv'
}





# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'bank_reviews'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

# Sentiment Analysis Configuration
SENTIMENT_CONFIG = {
    'model': os.getenv('SENTIMENT_MODEL', 'distilbert-base-uncased-finetuned-sst-2-english'),
    'use_vader': os.getenv('USE_VADER', 'false').lower() == 'true',
    'batch_size': 16
}

# Thematic Analysis Configuration
THEME_CONFIG = {
    'num_themes': int(os.getenv('NUM_THEMES', 5)),
    'max_features': 100,
    'ngram_range': (1, 3),  # unigrams, bigrams, trigrams
    'min_df': 2
}



# Visualization Configuration
VIZ_CONFIG = {
    'style': 'seaborn-v0_8-darkgrid',
    'figure_size': (12, 8),
    'dpi': 300,
    'color_palette': 'Set2'
}




# Predefined Theme Keywords (for manual clustering)
THEME_KEYWORDS = {
    'Account Access Issues': [
        'login', 'password', 'authentication', 'forgot', 'reset',
        'sign in', 'sign up', 'register', 'account', 'access'
    ],
    'Transaction Performance': [
        'transfer', 'slow', 'fast', 'speed', 'loading', 'payment',
        'transaction', 'delay', 'timeout', 'processing'
    ],
    'User Interface & Experience': [
        'ui', 'interface', 'design', 'layout', 'navigation', 'menu',
        'button', 'screen', 'display', 'easy', 'difficult', 'confusing'
    ],
    'Technical Issues': [
        'crash', 'bug', 'error', 'freeze', 'hang', 'broken',
        'not working', 'problem', 'issue', 'glitch', 'fail'
    ],
    'Customer Support': [
        'support', 'help', 'service', 'response', 'contact',
        'customer care', 'assistance', 'call center'
    ],
    'Feature Requests': [
        'feature', 'add', 'need', 'want', 'wish', 'should',
        'missing', 'would like', 'suggestion', 'improve'
    ],
    'Security & Privacy': [
        'security', 'safe', 'secure', 'privacy', 'fingerprint',
        'biometric', 'otp', 'verification', 'fraud'
    ]
}