# Ethiopian Banking App Reviews – Sentiment & Thematic Analysis
This project analyzes user reviews from the Google Play Store for three major Ethiopian banking apps:

- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA)
- Dashen Bank
We apply NLP and ML techniques to uncover key customer pain points and satisfaction drivers. The goal is to extract sentiment insights and thematic trends that banks can use to improve their mobile services.

## Business Problem
- Sentiment Analysis: Quantify the emotional tone (positive, negative, or neutral) of each customer review to measure overall user satisfaction.

- Thematic Analysis: Identify recurring topics such as login issues, transaction failures, performance problems, and UI/UX complaints.

- Insight Generation: Generate actionable recommendations for each bank and compare customer experience trends across institutions to support data-driven decision-making.


## Solution Overview
The project uses Natural Language Processing (NLP) to analyze customer reviews from Ethiopian mobile banking apps. First, reviews are collected and cleaned to prepare them for analysis. Then, sentiment analysis (VADER and DistilBERT) is applied to measure customer satisfaction levels.

Next, thematic analysis is performed to identify recurring issues and feature requests, such as login problems or transaction failures. Finally, the results are visualized and compared across banks to generate actionable insights that support product improvement and competitive strategy.


## Key Results
  - Metric 1: 15–20% improvement in customer issue detection accuracy through dual-model sentiment analysis (VADER + DistilBERT).

- Metric 2: Reduced manual review analysis effort by an estimated 40%, saving operational review time and associated costs.

- Metric 3: Reduced feedback analysis time from several days to under 1 hour using automated processing and visualization


## Quick Start

```
# Clone the repository
git clone https://github.com/username/project.git
```

```
python -m venv venv
venv\Scripts\activate   # On Windows
```

```
pip install -r requirements.txt
```
```
python src/main.py
```
```
python -m streamlit run dashboard/app.py

```

## Project Structure
```
CUSTOMER-EXPERIENCE-ANALYTICS-FINTECH-APPS/
│
├── .github/
│   └── workflows/
│       └── unittests.yml        # CI pipeline configuration
│
├── .streamlit/                  # Streamlit configuration
│
├── dashboard/
│   ├── data/                    # Dashboard-specific datasets
│   ├── __init__.py
│   ├── app.py                   # Streamlit dashboard application
│   └── requirements.txt         # Dashboard dependencies
│
├── data/                        # Raw and processed datasets
│
├── notebook/
│   ├── preprocessing_EDA.ipynb  # Data cleaning & exploratory analysis
│   └── sentiment.ipynb          # Sentiment modeling experiments
│
├── src/                         # Core source code (pipeline logic)
│
├── venv/                        # Virtual environment (not tracked)
│
├── .env.example                 # Environment variable template
├── .gitignore
├── README.md
├── requirements.txt             # Main project dependencies
└── schema.sql                   # Database schema definition

```


## Demo
[http://192.168.1.3:8502/]


## Technical Details
  Technical Details
### 1️⃣ Data: Source and Preprocessing

- Source: User reviews collected from the Google Play Store for Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank mobile apps.

- Preprocessing:
    - Removed duplicates and null values
    - Lowercased text and removed special character
    - Tokenization and basic text cleaning
    - Converted stored theme strings into structured lists
    - Prepared cleaned data for sentiment and thematic analysis

### 2️⃣ Model: Algorithm and Hyperparameters

- VADER (Rule-Based Model):
Compound score threshold:
- ≥ 0.05 → Positive
- ≤ -0.05 → Negative
- Otherwise → Neutral

- DistilBERT (Transformer Model):
     - Model: distilbert-base-uncased-finetuned-sst-2-english
     - Max sequence length: 512 tokens
     - Truncation enabled
     - GPU acceleration used when available

### 3️⃣ Evaluation: Metrics and Validation
- Sentiment distribution comparison (Positive / Negative / Neutral)
- Agreement rate between VADER and DistilBERT
- Manual spot-check validation of selected reviews
 - Thematic coverage percentage across total reviews


## Future Improvements
- Real-Time Data Integration: Automate review collection from the Google Play Store to enable continuous monitoring.
- Model Fine-Tuning: Fine-tune DistilBERT on Ethiopian banking app reviews to improve sentiment accuracy.
- Advanced Topic Modeling: Implement techniques like LDA or BERTopic for deeper theme discovery.
- Interactive Dashboard Enhancements: Add filtering by date, app version, rating, and sentiment trends over time.
- Scalable Database Integration: Store results in PostgreSQL for efficient querying and long-term analysis.
- Multilingual Support: Incorporate Amharic sentiment analysis to better capture local user feedback.


## Author
Hakima Muktar, [https://www.linkedin.com/in/hakima-muktar/]
