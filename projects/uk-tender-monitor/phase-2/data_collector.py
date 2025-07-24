#!/usr/bin/env python3
"""
UK Tender Monitor - Data Collection System
Hybrid approach: Export-first with API enhancement

Based on Phase 1 analysis:
- Export functions: 514 records vs 41 visible (25x improvement)
- Daily harvester: 243 records/day, 500+ OCDS fields
- Hybrid strategy maximizes data access while minimizing complexity
"""

import requests
import csv
import json
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UKTenderCollector:
    """Hybrid data collector for UK government tenders"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Base URLs from Phase 1 analysis
        self.base_url = "https://www.contractsfinder.service.gov.uk"
        self.search_url = f"{self.base_url}/Search"
        self.csv_export_url = f"{self.base_url}/Search/GetCsvFile"
        self.xml_export_url = f"{self.base_url}/Search/GetXmlFile"
        self.daily_harvester_url = f"{self.base_url}/Harvester/Notices/Data/CSV/Daily"
        
        # Initialize SQLite database
        self.db_path = self.data_dir / "tenders.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database with optimized schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tenders (
                    notice_identifier TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    organisation_name TEXT NOT NULL,
                    description TEXT,
                    status TEXT,
                    published_date TEXT,
                    closing_date TEXT,
                    value_low INTEGER,
                    value_high INTEGER,
                    contact_email TEXT,
                    postcode TEXT,
                    suitable_for_sme TEXT,
                    cpv_codes TEXT,
                    source_method TEXT,  -- 'export' or 'harvester'
                    collected_date TEXT,
                    raw_data TEXT,  -- JSON blob of all fields
                    UNIQUE(notice_identifier)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_published_date 
                ON tenders(published_date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_closing_date 
                ON tenders(closing_date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_organisation 
                ON tenders(organisation_name)
            """)
            
            logger.info(f"Database initialized at {self.db_path}")

    def search_and_export(self, keywords: str, format: str = "csv") -> Optional[Path]:
        """
        Perform search and download export file
        Based on Step 2 findings: 514 records vs 41 visible (25x improvement)
        """
        logger.info(f"Searching for: '{keywords}' (format: {format})")
        
        # Step 1: Perform search to set session state
        search_params = {
            'Keywords': keywords,
            'Status': '',  # All statuses
            'Stage': '',   # All stages
            'Nationwide': '',
            'Postcode': '',
            'OrganisationName': '',
            'NoticeType': '',
            'Size': '',
            'ValueMin': '',
            'ValueMax': ''
        }
        
        try:
            # Initialize search session
            search_response = requests.get(self.search_url, params=search_params, timeout=30)
            search_response.raise_for_status()
            logger.info(f"Search session initialized (status: {search_response.status_code})")
            
            # Step 2: Download export file using session state
            export_url = self.csv_export_url if format == "csv" else self.xml_export_url
            
            # Use same session to inherit search parameters
            session = requests.Session()
            session.get(self.search_url, params=search_params)
            
            export_response = session.get(export_url, timeout=60)
            export_response.raise_for_status()
            
            # Save export file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{keywords.replace(' ', '_')}_{timestamp}.{format}"
            file_path = self.data_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(export_response.content)
                
            file_size = file_path.stat().st_size
            logger.info(f"Export saved: {file_path} ({file_size:,} bytes)")
            
            return file_path
            
        except requests.RequestException as e:
            logger.error(f"Export failed: {e}")
            return None

    def collect_daily_harvester(self) -> Optional[Path]:
        """
        Collect daily harvester data
        Based on Step 3 findings: 243 records/day, 500+ OCDS fields
        """
        logger.info("Collecting daily harvester data...")
        
        try:
            response = requests.get(self.daily_harvester_url, timeout=120)
            response.raise_for_status()
            
            # Save daily harvest
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"daily_harvest_{date_str}.csv"
            file_path = self.data_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
                
            file_size = file_path.stat().st_size
            logger.info(f"Daily harvest saved: {file_path} ({file_size:,} bytes)")
            
            return file_path
            
        except requests.RequestException as e:
            logger.error(f"Daily harvest failed: {e}")
            return None

    def process_csv_export(self, csv_path: Path, source_method: str = "export") -> int:
        """
        Process CSV file and store in database
        Handles both export format and OCDS harvester format
        """
        logger.info(f"Processing CSV: {csv_path}")
        
        records_processed = 0
        records_inserted = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # Check if this is OCDS format (harvester) or export format
                fieldnames = reader.fieldnames or []
                is_ocds = any('releases/0/' in field for field in fieldnames)
                
                with sqlite3.connect(self.db_path) as conn:
                    for row in reader:
                        records_processed += 1
                        
                        if is_ocds:
                            # OCDS harvester format
                            tender_data = self._extract_ocds_data(row, source_method)
                        else:
                            # Export format
                            tender_data = self._extract_export_data(row, source_method)
                        
                        # Skip records without essential data
                        if not tender_data['notice_identifier'] or not tender_data['title']:
                            continue
                            
                        try:
                            conn.execute("""
                                INSERT OR REPLACE INTO tenders 
                                (notice_identifier, title, organisation_name, description, 
                                 status, published_date, closing_date, value_low, value_high,
                                 contact_email, postcode, suitable_for_sme, cpv_codes,
                                 source_method, collected_date, raw_data)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, tuple(tender_data.values()))
                            
                            records_inserted += 1
                            
                        except sqlite3.Error as e:
                            logger.warning(f"Database insert failed for {tender_data['notice_identifier']}: {e}")
                            continue
            
            logger.info(f"Processed {records_processed} records, inserted {records_inserted}")
            return records_inserted
            
        except Exception as e:
            logger.error(f"CSV processing failed: {e}")
            return 0

    def _extract_export_data(self, row: Dict, source_method: str) -> Dict:
        """Extract data from export CSV format"""
        return {
            'notice_identifier': row.get('Notice Identifier', '').strip(),
            'title': row.get('Title', '').strip(),
            'organisation_name': row.get('Organisation Name', '').strip(),
            'description': row.get('Description', '').strip(),
            'status': row.get('Status', '').strip(),
            'published_date': row.get('Published Date', '').strip(),
            'closing_date': row.get('Closing Date', '').strip(),
            'value_low': self._parse_value(row.get('Value Low', '')),
            'value_high': self._parse_value(row.get('Value High', '')),
            'contact_email': row.get('Contact Email', '').strip(),
            'postcode': row.get('Postcode', '').strip(),
            'suitable_for_sme': row.get('Suitable for SME', '').strip(),
            'cpv_codes': row.get('CPV Codes', '').strip(),
            'source_method': source_method,
            'collected_date': datetime.now().isoformat(),
            'raw_data': json.dumps(dict(row))
        }

    def _extract_ocds_data(self, row: Dict, source_method: str) -> Dict:
        """Extract data from OCDS harvester format"""
        # OCDS uses hierarchical field names like releases/0/tender/title
        return {
            'notice_identifier': row.get('releases/0/id', '').strip(),
            'title': row.get('releases/0/tender/title', '').strip(),
            'organisation_name': row.get('releases/0/parties/0/name', '').strip(),
            'description': row.get('releases/0/tender/description', '').strip(),
            'status': row.get('releases/0/tender/status', '').strip(),
            'published_date': row.get('releases/0/date', '').strip(),
            'closing_date': row.get('releases/0/tender/tenderPeriod/endDate', '').strip(),
            'value_low': self._parse_value(row.get('releases/0/tender/minValue/amount', '')),
            'value_high': self._parse_value(row.get('releases/0/tender/value/amount', '')),
            'contact_email': row.get('releases/0/parties/0/contactPoint/email', '').strip(),
            'postcode': row.get('releases/0/parties/0/address/postalCode', '').strip(),
            'suitable_for_sme': row.get('releases/0/tender/suitability/sme', '').strip(),
            'cpv_codes': row.get('releases/0/tender/classification/id', '').strip(),
            'source_method': source_method,
            'collected_date': datetime.now().isoformat(),
            'raw_data': json.dumps(dict(row))
        }

    def _parse_value(self, value_str: str) -> Optional[int]:
        """Parse monetary value strings"""
        if not value_str or value_str.strip() == '':
            return None
            
        # Remove currency symbols and commas
        cleaned = value_str.replace('£', '').replace(',', '').strip()
        
        try:
            return int(float(cleaned))
        except (ValueError, TypeError):
            return None

    def filter_digital_transformation(self, min_value: int = 10000) -> List[Dict]:
        """
        Filter for high-relevance digital transformation opportunities
        Based on Step 2 sample analysis: Healthcare, Local Gov, Central Gov priority
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM tenders 
                WHERE (
                    (description LIKE '%digital transformation%' 
                     OR description LIKE '%digital%modernisation%'
                     OR description LIKE '%cloud migration%'
                     OR description LIKE '%digital infrastructure%'
                     OR description LIKE '%API%'
                     OR description LIKE '%automation%'
                     OR description LIKE '%workflow%'
                     OR description LIKE '%data integration%')
                    AND (value_high IS NULL OR value_high >= ?)
                    AND status = 'Open'
                )
                ORDER BY value_high DESC NULLS LAST, closing_date ASC
            """, (min_value,))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total records
            cursor = conn.execute("SELECT COUNT(*) FROM tenders")
            stats['total_records'] = cursor.fetchone()[0]
            
            # By source method
            cursor = conn.execute("""
                SELECT source_method, COUNT(*) 
                FROM tenders 
                GROUP BY source_method
            """)
            stats['by_source'] = dict(cursor.fetchall())
            
            # Open vs closed
            cursor = conn.execute("""
                SELECT status, COUNT(*) 
                FROM tenders 
                GROUP BY status
            """)
            stats['by_status'] = dict(cursor.fetchall())
            
            # Value distribution
            cursor = conn.execute("""
                SELECT 
                    COUNT(CASE WHEN value_high >= 1000000 THEN 1 END) as high_value,
                    COUNT(CASE WHEN value_high BETWEEN 100000 AND 999999 THEN 1 END) as medium_value,
                    COUNT(CASE WHEN value_high < 100000 THEN 1 END) as low_value,
                    COUNT(CASE WHEN value_high IS NULL THEN 1 END) as no_value
                FROM tenders
            """)
            result = cursor.fetchone()
            stats['value_distribution'] = {
                'high_value_1M+': result[0],
                'medium_value_100K-1M': result[1], 
                'low_value_under_100K': result[2],
                'no_value_specified': result[3]
            }
            
            return stats

    def run_full_collection(self, keywords: str = "digital transformation") -> Dict:
        """
        Run complete collection process
        Implements hybrid approach from Step 3 recommendations
        """
        logger.info("Starting full collection process...")
        
        results = {
            'export_records': 0,
            'harvester_records': 0,
            'total_processed': 0,
            'errors': []
        }
        
        # Phase 1: Export-based targeted collection
        try:
            export_file = self.search_and_export(keywords)
            if export_file:
                results['export_records'] = self.process_csv_export(export_file, "export")
            else:
                results['errors'].append("Export collection failed")
        except Exception as e:
            results['errors'].append(f"Export phase error: {e}")
            
        # Phase 2: Daily harvester collection
        try:
            harvester_file = self.collect_daily_harvester()
            if harvester_file:
                results['harvester_records'] = self.process_csv_export(harvester_file, "harvester")
            else:
                results['errors'].append("Harvester collection failed")
        except Exception as e:
            results['errors'].append(f"Harvester phase error: {e}")
            
        results['total_processed'] = results['export_records'] + results['harvester_records']
        
        logger.info(f"Collection complete: {results['total_processed']} total records")
        return results


if __name__ == "__main__":
    # Initialize collector
    collector = UKTenderCollector()
    
    # Run full collection
    results = collector.run_full_collection("digital transformation")
    
    # Display results
    print(f"\n=== Collection Results ===")
    print(f"Export records: {results['export_records']}")
    print(f"Harvester records: {results['harvester_records']}")
    print(f"Total processed: {results['total_processed']}")
    
    if results['errors']:
        print(f"Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")
    
    # Get statistics
    stats = collector.get_collection_stats()
    print(f"\n=== Database Statistics ===")
    print(f"Total records: {stats['total_records']}")
    print(f"By source: {stats['by_source']}")
    print(f"By status: {stats['by_status']}")
    print(f"Value distribution: {stats['value_distribution']}")
    
    # Show top opportunities
    opportunities = collector.filter_digital_transformation(50000)
    print(f"\n=== Top Digital Transformation Opportunities ===")
    for i, opp in enumerate(opportunities[:5], 1):
        value_str = f"£{opp['value_high']:,}" if opp['value_high'] else "Value TBD"
        print(f"{i}. {opp['title'][:60]}...")
        print(f"   {opp['organisation_name']} | {value_str} | Closes: {opp['closing_date']}")