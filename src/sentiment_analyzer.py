"""
Sentiment Analysis Module
Task 2: Sentiment Analysis

This module provides sentiment analysis using two approaches:
1. VADER (Valence Aware Dictionary and sEntiment Reasoner) - Rule-based
2. DistilBERT - Transformer-based deep learning model

Why two methods?
- VADER: Fast, lightweight, good for social media text, no GPU needed
- DistilBERT: More accurate, understands context, but slower and heavier
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

from config import SENTIMENT_CONFIG, DATA_PATHS


class SentimentAnalyzer:
    """
    Sentiment Analyzer class supporting VADER and DistilBERT methods.
    
    Purpose:
    - Classify reviews as Positive, Negative, or Neutral
    - Provide confidence scores for each classification
    - Enable comparison between rule-based and ML approaches
    """

    def __init__(self, method='vader'):
        """
        Initialize the sentiment analyzer.
        
        Args:
            method (str): 'vader' for rule-based or 'distilbert' for transformer-based
        """
        self.method = method.lower()
        self.model = None
        self.tokenizer = None
        
        # Initialize the appropriate analyzer
        if self.method == 'vader':
            self._init_vader()
        elif self.method == 'distilbert':
            self._init_distilbert()
        else:
            raise ValueError(f"Unknown method: {method}. Use 'vader' or 'distilbert'")
    
    def _init_vader(self):
        """
        Initialize VADER sentiment analyzer.
        
        What is VADER?
        - Rule-based sentiment analysis tool
        - Specifically tuned for social media and short texts
        - Uses a lexicon (dictionary) of words with sentiment scores
        - Handles emojis, slang, and punctuation (e.g., "GREAT!!!" is more positive than "great")
        """
        print("Initializing VADER sentiment analyzer...")
        self.model = SentimentIntensityAnalyzer()
        print("VADER ready!")
    
    def _init_distilbert(self):
        """
        Initialize DistilBERT sentiment analyzer.
        
        What is DistilBERT?
        - A smaller, faster version of BERT (Bidirectional Encoder Representations from Transformers)
        - Pre-trained on millions of text samples
        - Fine-tuned on SST-2 (Stanford Sentiment Treebank) for sentiment classification
        - Understands context: "not good" = negative, even though "good" is positive
        """
        print("Initializing DistilBERT sentiment analyzer...")
        print("(This may take a moment to download the model on first run)")
        
        model_name = SENTIMENT_CONFIG['model']
        
        # Check if GPU is available
        device = 0 if torch.cuda.is_available() else -1
        if device == 0:
            print("Using GPU for inference")
        else:
            print("Using CPU for inference")
        
        # Load the sentiment analysis pipeline
        self.model = pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name,
            device=device,
            truncation=True,
            max_length=512  # DistilBERT max token limit
        )
        print("DistilBERT ready!")
    
    def analyze_text(self, text):
        """
        Analyze sentiment of a single text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Contains 'label' (POSITIVE/NEGATIVE/NEUTRAL) and 'score' (confidence 0-1)
        """
        if not text or pd.isna(text) or len(str(text).strip()) == 0:
            return {'label': 'NEUTRAL', 'score': 0.0}
        
        text = str(text).strip()
        
        if self.method == 'vader':
            return self._analyze_vader(text)
        else:
            return self._analyze_distilbert(text)
    
    def _analyze_vader(self, text):
        """
        Analyze sentiment using VADER.
        
        How VADER scoring works:
        - Returns 4 scores: neg, neu, pos, compound
        - Compound score ranges from -1 (most negative) to +1 (most positive)
        - Thresholds: compound >= 0.05 = Positive, <= -0.05 = Negative, else Neutral
        """
        scores = self.model.polarity_scores(text)
        compound = scores['compound']
        
        # Determine label based on compound score
        if compound >= 0.05:
            label = 'POSITIVE'
            score = scores['pos']  # Use positive component as confidence
        elif compound <= -0.05:
            label = 'NEGATIVE'
            score = scores['neg']  # Use negative component as confidence
        else:
            label = 'NEUTRAL'
            score = scores['neu']  # Use neutral component as confidence
        
        return {
            'label': label,
            'score': round(abs(compound), 4),  # Use absolute compound as overall confidence
            'compound': compound,  # Keep raw compound for detailed analysis
            'pos': scores['pos'],
            'neg': scores['neg'],
            'neu': scores['neu']
        }
    
    def _analyze_distilbert(self, text):
        """
        Analyze sentiment using DistilBERT.
        
        How DistilBERT works:
        - Tokenizes text into subwords
        - Passes through transformer layers to understand context
        - Outputs probability distribution over POSITIVE/NEGATIVE
        - Returns the label with highest probability
        """
        try:
            # Truncate very long texts to avoid memory issues
            if len(text) > 2000:
                text = text[:2000]
            
            result = self.model(text)[0]
            
            return {
                'label': result['label'],
                'score': round(result['score'], 4)
            }
        except Exception as e:
            print(f"Error analyzing text: {str(e)[:50]}")
            return {'label': 'NEUTRAL', 'score': 0.0}
    
    def analyze_dataframe(self, df, text_column='review_text', batch_size=None):
        """
        Analyze sentiment for all reviews in a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame containing reviews
            text_column (str): Name of the column containing review text
            batch_size (int): Batch size for processing (default from config)
            
        Returns:
            pd.DataFrame: Original DataFrame with added sentiment columns
        """
        if batch_size is None:
            batch_size = SENTIMENT_CONFIG.get('batch_size', 16)
        
        print(f"\nAnalyzing sentiment for {len(df)} reviews using {self.method.upper()}...")
        print("=" * 60)
        
        # Initialize result lists
        labels = []
        scores = []
        
        # Process reviews with progress bar
        for idx, text in tqdm(enumerate(df[text_column]), total=len(df), desc="Analyzing"):
            result = self.analyze_text(text)
            labels.append(result['label'])
            scores.append(result['score'])
        
        # Add results to DataFrame
        result_df = df.copy()
        result_df[f'sentiment_label_{self.method}'] = labels
        result_df[f'sentiment_score_{self.method}'] = scores
        
        # Print summary
        self._print_summary(result_df, f'sentiment_label_{self.method}')
        
        return result_df
    
    def _print_summary(self, df, label_column):
        """Print sentiment analysis summary statistics."""
        print("\n" + "=" * 60)
        print("SENTIMENT ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Overall distribution
        print(f"\nOverall Sentiment Distribution ({self.method.upper()}):")
        sentiment_counts = df[label_column].value_counts()
        total = len(df)
        for label, count in sentiment_counts.items():
            pct = (count / total) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")
        
        # By bank
        if 'bank_name' in df.columns:
            print(f"\nSentiment by Bank:")
            for bank in df['bank_name'].unique():
                bank_df = df[df['bank_name'] == bank]
                pos_count = len(bank_df[bank_df[label_column] == 'POSITIVE'])
                neg_count = len(bank_df[bank_df[label_column] == 'NEGATIVE'])
                pos_pct = (pos_count / len(bank_df)) * 100
                neg_pct = (neg_count / len(bank_df)) * 100
                print(f"  {bank}:")
                print(f"    Positive: {pos_pct:.1f}% | Negative: {neg_pct:.1f}%")


def analyze_reviews_vader(input_path=None, output_path=None):
    """
    Convenience function to run VADER sentiment analysis on reviews.
    
    Args:
        input_path (str): Path to processed reviews CSV
        output_path (str): Path to save results
        
    Returns:
        pd.DataFrame: Reviews with VADER sentiment scores
    """
    input_path = input_path or DATA_PATHS['processed_reviews']
    output_path = output_path or DATA_PATHS['sentiment_results']
    
    # Load data
    print(f"Loading reviews from {input_path}...")
    df = pd.read_csv(input_path)
    
    # Analyze
    analyzer = SentimentAnalyzer(method='vader')
    result_df = analyzer.analyze_dataframe(df)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df.to_csv(output_path, index=False)
    print(f"\nResults saved to {output_path}")
    
    return result_df


def analyze_reviews_distilbert(input_path=None, output_path=None):
    """
    Convenience function to run DistilBERT sentiment analysis on reviews.
    
    Args:
        input_path (str): Path to processed reviews CSV (or with VADER results)
        output_path (str): Path to save results
        
    Returns:
        pd.DataFrame: Reviews with DistilBERT sentiment scores
    """
    input_path = input_path or DATA_PATHS['sentiment_results']  # Use VADER results as input
    output_path = output_path or DATA_PATHS['sentiment_results']
    
    # Load data
    print(f"Loading reviews from {input_path}...")
    df = pd.read_csv(input_path)
    
    # Analyze
    analyzer = SentimentAnalyzer(method='distilbert')
    result_df = analyzer.analyze_dataframe(df)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df.to_csv(output_path, index=False)
    print(f"\nResults saved to {output_path}")
    
    return result_df


def main():
    """
    Main function to run both sentiment analyses sequentially.
    
    Pipeline:
    1. Load processed reviews
    2. Run VADER analysis (fast)
    3. Run DistilBERT analysis (accurate)
    4. Save combined results for comparison
    """
    print("=" * 60)
    print("SENTIMENT ANALYSIS PIPELINE")
    print("=" * 60)
    
    # Step 1: VADER Analysis
    print("\n[1/2] Running VADER Sentiment Analysis...")
    df_vader = analyze_reviews_vader()
    
    # Step 2: DistilBERT Analysis
    print("\n[2/2] Running DistilBERT Sentiment Analysis...")
    df_final = analyze_reviews_distilbert()
    
    # Summary comparison
    print("\n" + "=" * 60)
    print("COMPARISON: VADER vs DistilBERT")
    print("=" * 60)
    
    # Agreement rate
    if 'sentiment_label_vader' in df_final.columns and 'sentiment_label_distilbert' in df_final.columns:
        agreement = (df_final['sentiment_label_vader'] == df_final['sentiment_label_distilbert']).mean()
        print(f"\nAgreement rate: {agreement * 100:.1f}%")
    
    print("\n✓ Sentiment analysis complete!")
    return df_final


if __name__ == "__main__":
    result = main()