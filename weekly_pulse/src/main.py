import argparse
import logging
import sqlite3
import datetime
import os
import json
from scraper import PlayStoreScraper
from normalizer import ReviewNormalizer
from analyzer import AnalysisEngine
from renderer import PulseRenderer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("weekly_pulse")

def init_db(db_path: str = 'pulse_audit.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            iso_week TEXT PRIMARY KEY,
            run_date TEXT,
            doc_anchor TEXT,
            email_id TEXT
        )
    ''')
    conn.commit()
    return conn

def check_idempotency(conn, iso_week: str) -> bool:
    cursor = conn.cursor()
    cursor.execute('SELECT doc_anchor FROM runs WHERE iso_week = ?', (iso_week,))
    return cursor.fetchone() is not None

def log_run(conn, iso_week: str, doc_anchor: str, email_id: str):
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO runs (iso_week, run_date, doc_anchor, email_id) VALUES (?, ?, ?, ?)',
        (iso_week, datetime.datetime.now().isoformat(), doc_anchor, email_id)
    )
    conn.commit()

def main():
    parser = argparse.ArgumentParser(description="Weekly Product Review Pulse (Groww)")
    parser.add_argument("--weeks", type=int, default=8, help="Number of weeks back to scrape")
    parser.add_argument("--iso-week", type=str, help="Target ISO week (e.g., 2026-W42). Defaults to current.")
    parser.add_argument("--db-path", type=str, default="pulse_audit.db", help="Path to audit DB")
    
    args = parser.parse_args()
    
    # Calculate ISO week if not provided
    if not args.iso_week:
        now = datetime.datetime.now()
        year, week, _ = now.isocalendar()
        target_iso_week = f"{year}-W{week:02d}"
    else:
        target_iso_week = args.iso_week
        
    logger.info("Starting Weekly Pulse Pipeline")
    logger.info(f"Target ISO Week: {target_iso_week}")
    
    conn = init_db(args.db_path)
    if check_idempotency(conn, target_iso_week):
        logger.warning(f"Pipeline already ran for {target_iso_week}. Exiting to prevent duplicates.")
        return
        
    # Phase 1: Ingestion
    scraper = PlayStoreScraper()
    raw_reviews = scraper.fetch_reviews(weeks_back=args.weeks, max_results=50000) # Full limit
    
    if not raw_reviews:
        logger.warning("No reviews fetched.")
        return
        
    # Normalization
    reviews = ReviewNormalizer.normalize(raw_reviews)
    if not reviews:
        logger.warning("All fetched reviews were filtered out during normalization.")
        return
        
    # Save raw reviews to data folder
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    normalized_data_path = os.path.join(data_dir, f"normalized_reviews_{target_iso_week}.json")
    with open(normalized_data_path, "w", encoding="utf-8") as f:
        json_data = [json.loads(r.model_dump_json()) for r in reviews]
        json.dump(json_data, f, indent=2)
    logger.info(f"Saved {len(reviews)} normalized reviews to {normalized_data_path}")
        
    # Phase 2: Analysis
    if not os.environ.get("GROQ_API_KEY"):
        logger.warning("GROQ_API_KEY not set. Mocking analysis for dry-run.")
        analysis_data = {
            "themes": ["App performance & bugs", "Customer support friction"],
            "quotes": ["The app freezes often.", "Support takes days to reply."],
            "actions": ["Stabilise peak-time performance", "Improve support SLA"]
        }
    else:
        analyzer = AnalysisEngine()
        analysis_data = analyzer.process(reviews)
    
    # Phase 4: Rendering
    renderer = PulseRenderer()
    doc_content = renderer.render_doc_content(target_iso_week, analysis_data)
    
    # Phase 4/3: Delivery via MCP Servers
    logger.info("Sending payload to Google Docs MCP Server (Mocked)...")
    mock_doc_anchor = f"https://docs.google.com/document/d/mock/edit#heading={target_iso_week}"
    
    email_html = renderer.render_email_teaser(target_iso_week, analysis_data, mock_doc_anchor)
    logger.info("Sending payload to Gmail MCP Server (Mocked)...")
    mock_email_id = f"msg_{target_iso_week}_draft"
    
    # Audit Logging
    log_run(conn, target_iso_week, mock_doc_anchor, mock_email_id)
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
