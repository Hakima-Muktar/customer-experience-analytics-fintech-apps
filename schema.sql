
-- Bank Reviews Database Schema
-- Created for Customer Experience Analytics Project

-- Banks Table
-- Stores information about the three Ethiopian banks
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_code VARCHAR(20) UNIQUE NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    app_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews Table
-- Stores scraped reviews with sentiment and theme analysis
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id),
    review_text TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_date DATE,
    sentiment_label_vader VARCHAR(20),
    sentiment_score_vader FLOAT,
    sentiment_label_distilbert VARCHAR(20),
    sentiment_score_distilbert FLOAT,
    themes TEXT,
    primary_theme VARCHAR(100),
    source VARCHAR(50) DEFAULT 'Google Play',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_label_distilbert);
CREATE INDEX IF NOT EXISTS idx_reviews_theme ON reviews(primary_theme);

-- Sample Queries

-- Count reviews per bank
-- SELECT b.bank_name, COUNT(r.review_id) as review_count
-- FROM banks b
-- LEFT JOIN reviews r ON b.bank_id = r.bank_id
-- GROUP BY b.bank_name;

-- Average rating per bank
-- SELECT b.bank_name, ROUND(AVG(r.rating)::numeric, 2) as avg_rating
-- FROM banks b
-- JOIN reviews r ON b.bank_id = r.bank_id
-- GROUP BY b.bank_name;

-- Sentiment distribution
-- SELECT sentiment_label_distilbert, COUNT(*) as count
-- FROM reviews
-- GROUP BY sentiment_label_distilbert;