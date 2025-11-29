## Methodology
This project involves scraping, preprocessing, and analyzing reviews from Ethiopian mobile banking apps. The workflow consists of the following steps:
1. **Scraping Data**
   - Reviews are collected from Google Play Store using the `google_play_scraper` Python library.
   - Target apps include:
     - Dashen Bank 
     - Commercial Bank of Ethiopia 
     - Abyssinia Bank 
   - The scraped data includes: user name, review text, rating, review date, and app package.
2. **Preprocessing Data**
   - Loaded raw reviews into a Pandas DataFrame.
   - Checked and handled missing values in critical columns: `review_text`, `rating`, `bank_name`.
   - Removed duplicate reviews.
   - Normalized review dates to `YYYY-MM-DD` format and extracted `review_year` and `review_month`.
   - Cleaned review text by removing extra whitespaces and empty reviews.
   - Validated ratings (1-5 stars) and removed invalid entries.
   - Added additional columns for consistent format: `thumbs_up`, `reply_content`, `source`, `review_id`.
3. **Saving Processed Data**
   - Processed data is saved as a CSV file (`reviews_processed.csv`) under the `data/processed` folder for further analysis.
4. **Analysis & Visualization**
   - Generated distributions of ratings per bank.
   - Counted reviews per bank.
   - Visualized results using `matplotlib` and `seaborn`.
