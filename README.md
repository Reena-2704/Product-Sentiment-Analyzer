# Product Sentiment Analyzer — URL Auto Review Version

This version changes the dashboard so the user enters a **product/review page URL**, not a product name or manual reviews.

## New flow

Product Link → Selenium + BeautifulSoup → Reviews → TextBlob → Dashboard

## Run backend

Open PowerShell 1:

```powershell
cd C:\Users\Asus\Downloads\Product_Sentiment_Analyzer_URL_Auto\backend
..\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Backend:
http://127.0.0.1:5000

## Run frontend

Open PowerShell 2:

```powershell
cd C:\Users\Asus\Downloads\Product_Sentiment_Analyzer_URL_Auto\frontend
npm install
npm run dev
```

Open:
http://localhost:5173

## Dashboard usage

1. Paste a product/review page URL.
2. Click **Fetch & Analyze**.
3. The backend opens the page with Selenium.
4. It tries common review selectors.
5. It automatically extracts the product name.
6. TextBlob classifies every collected review as Positive, Neutral, or Negative.
7. The dashboard displays counts, percentages, charts, review text, ratings and polarity.
8. Export CSV downloads analyzed reviews.

## Important scraping limitation

Different websites have different HTML structures and anti-bot rules. Some require login or additional interaction. This project uses common selectors, but a site-specific scraper may be needed for a particular website.

Only scrape pages you are authorized to access and respect the site's terms and applicable rules.

### Browser tab logo
The frontend includes `frontend/public/favicon.png` and `frontend/public/sentiment-logo.png`. Vite serves the favicon automatically at `/favicon.png`.


## PDF feature coverage
This version implements the PDF requirements: Selenium + BeautifulSoup dynamic scraping, TextBlob sentiment classification, React + Recharts visualization, Flask APIs, MongoDB/local fallback, sentiment distribution, sentiment overview, historical sentiment trends, word-frequency analytics, CSV export, and deployment configuration for Render + Vercel.

### Local run
Backend: `cd backend` -> activate venv -> `pip install -r requirements.txt` -> `python app.py`
Frontend: `cd frontend` -> `npm install` -> `npm run dev`

### MongoDB Atlas
Create a MongoDB Atlas database and set `MONGODB_URI` in `backend/.env`. The application timestamps saved reviews for historical trend analysis. Without MongoDB, local in-memory storage is used.

### Cloud deployment
Backend: deploy the `backend` directory to Render using `gunicorn app:app`; set `MONGODB_URI`, `MONGODB_DATABASE`, and `MONGODB_COLLECTION`.
Frontend: deploy the `frontend` directory to Vercel/Netlify. For a hosted frontend, change the `API` constant in `frontend/src/App.jsx` to the deployed backend URL.

### Note
Cloud hosting is configuration-ready but cannot be considered deployed until you create the services/accounts and deploy them. Scraping behavior varies by website and may require site-specific selectors or permitted access.
