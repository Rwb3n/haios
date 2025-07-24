#!/usr/bin/env python3
"""
UK Tender Monitor - Change Detection and Monitoring System
Implements intelligent change detection and automated monitoring
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
from data_collector import UKTenderCollector

logger = logging.getLogger(__name__)

class TenderMonitor:
    """Intelligent monitoring system with change detection"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.collector = UKTenderCollector(data_dir)
        self.changes_db = self.data_dir / "changes.db"
        self.init_changes_database()
        
    def init_changes_database(self):
        """Initialize change tracking database"""
        with sqlite3.connect(self.changes_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS change_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notice_identifier TEXT NOT NULL,
                    change_type TEXT NOT NULL,  -- 'new', 'updated', 'closed', 'value_changed'
                    old_value TEXT,
                    new_value TEXT,
                    detected_date TEXT NOT NULL,
                    priority_score INTEGER DEFAULT 0,
                    notified BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collection_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date TEXT NOT NULL,
                    records_collected INTEGER,
                    new_records INTEGER,
                    updated_records INTEGER,
                    data_hash TEXT,
                    run_duration_seconds REAL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_change_date 
                ON change_log(detected_date)
            """)
            
            logger.info("Change tracking database initialized")

    def detect_changes(self, keywords: str = "digital transformation") -> Dict:
        """
        Detect changes since last collection
        Returns summary of new, updated, and closed opportunities
        """
        start_time = datetime.now()
        logger.info("Starting change detection...")
        
        # Get snapshot of current data state
        current_state = self._get_current_state()
        
        # Run new collection
        collection_results = self.collector.run_full_collection(keywords)
        
        # Get new data state
        new_state = self._get_current_state()
        
        # Analyze changes
        changes = self._analyze_state_changes(current_state, new_state)
        
        # Log collection run
        run_duration = (datetime.now() - start_time).total_seconds()
        self._log_collection_run(
            collection_results['total_processed'],
            changes['new_count'],
            changes['updated_count'],
            new_state['data_hash'],
            run_duration
        )
        
        # Record individual changes
        self._record_changes(changes['changes'])
        
        logger.info(f"Change detection complete in {run_duration:.1f}s")
        return changes

    def _get_current_state(self) -> Dict:
        """Get current state of tender database"""
        with sqlite3.connect(self.collector.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT notice_identifier, title, status, value_high, 
                       closing_date, published_date, raw_data
                FROM tenders
            """)
            
            records = {}
            raw_data = []
            
            for row in cursor:
                record_id = row['notice_identifier']
                records[record_id] = {
                    'title': row['title'],
                    'status': row['status'],
                    'value_high': row['value_high'],
                    'closing_date': row['closing_date'],
                    'published_date': row['published_date']
                }
                raw_data.append(row['raw_data'])
            
            # Create hash of all data for change detection
            data_str = json.dumps(sorted(raw_data), sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()[:16]
            
            return {
                'records': records,
                'data_hash': data_hash,
                'record_count': len(records)
            }

    def _analyze_state_changes(self, old_state: Dict, new_state: Dict) -> Dict:
        """Analyze differences between old and new states"""
        old_records = old_state['records']
        new_records = new_state['records']
        
        old_ids = set(old_records.keys())
        new_ids = set(new_records.keys())
        
        # Identify change types
        new_notices = new_ids - old_ids
        removed_notices = old_ids - new_ids  # Shouldn't happen with gov data
        common_notices = old_ids & new_ids
        
        changes = []
        
        # New notices
        for notice_id in new_notices:
            changes.append({
                'notice_identifier': notice_id,
                'change_type': 'new',
                'old_value': None,
                'new_value': json.dumps(new_records[notice_id]),
                'priority_score': self._calculate_priority(new_records[notice_id])
            })
        
        # Updated notices
        for notice_id in common_notices:
            old_record = old_records[notice_id]
            new_record = new_records[notice_id]
            
            # Check for status changes
            if old_record['status'] != new_record['status']:
                changes.append({
                    'notice_identifier': notice_id,
                    'change_type': 'status_changed',
                    'old_value': old_record['status'],
                    'new_value': new_record['status'],
                    'priority_score': 7 if new_record['status'] == 'Closed' else 5
                })
            
            # Check for value changes
            if old_record['value_high'] != new_record['value_high']:
                changes.append({
                    'notice_identifier': notice_id,
                    'change_type': 'value_changed',
                    'old_value': str(old_record['value_high']),
                    'new_value': str(new_record['value_high']),
                    'priority_score': 6
                })
            
            # Check for closing date changes
            if old_record['closing_date'] != new_record['closing_date']:
                changes.append({
                    'notice_identifier': notice_id,
                    'change_type': 'closing_date_changed',
                    'old_value': old_record['closing_date'],
                    'new_value': new_record['closing_date'],
                    'priority_score': 8  # High priority - deadline change
                })
        
        return {
            'changes': changes,
            'new_count': len(new_notices),
            'updated_count': len([c for c in changes if c['change_type'] != 'new']),
            'total_changes': len(changes),
            'data_changed': old_state['data_hash'] != new_state['data_hash']
        }

    def _calculate_priority(self, record: Dict) -> int:
        """Calculate priority score for a tender (1-10, 10 = highest)"""
        score = 5  # Base score
        
        # High value contracts get higher priority
        value = record.get('value_high')
        if value:
            if value >= 1000000:      # £1M+
                score += 3
            elif value >= 100000:     # £100K+
                score += 2
            elif value >= 50000:      # £50K+
                score += 1
        
        # Status-based scoring
        if record.get('status') == 'Open':
            score += 1
        
        # Closing date urgency
        closing_date = record.get('closing_date')
        if closing_date:
            try:
                closing_dt = datetime.fromisoformat(closing_date.replace('Z', '+00:00'))
                days_to_close = (closing_dt - datetime.now()).days
                if days_to_close <= 7:        # Closing within a week
                    score += 2
                elif days_to_close <= 30:     # Closing within a month
                    score += 1
            except (ValueError, TypeError):
                pass
        
        return min(score, 10)  # Cap at 10

    def _record_changes(self, changes: List[Dict]):
        """Record changes in the changes database"""
        if not changes:
            return
            
        with sqlite3.connect(self.changes_db) as conn:
            for change in changes:
                conn.execute("""
                    INSERT INTO change_log 
                    (notice_identifier, change_type, old_value, new_value, 
                     detected_date, priority_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    change['notice_identifier'],
                    change['change_type'],
                    change['old_value'],
                    change['new_value'],
                    datetime.now().isoformat(),
                    change['priority_score']
                ))
            
            logger.info(f"Recorded {len(changes)} changes")

    def _log_collection_run(self, records_collected: int, new_records: int, 
                           updated_records: int, data_hash: str, duration: float):
        """Log collection run statistics"""
        with sqlite3.connect(self.changes_db) as conn:
            conn.execute("""
                INSERT INTO collection_runs 
                (run_date, records_collected, new_records, updated_records, 
                 data_hash, run_duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                records_collected,
                new_records,
                updated_records,
                data_hash,
                duration
            ))

    def get_high_priority_changes(self, since_hours: int = 24) -> List[Dict]:
        """Get high-priority changes from the last N hours"""
        since_date = (datetime.now() - timedelta(hours=since_hours)).isoformat()
        
        # Query changes database first
        with sqlite3.connect(self.changes_db) as changes_conn:
            changes_conn.row_factory = sqlite3.Row
            cursor = changes_conn.execute("""
                SELECT notice_identifier, change_type, old_value, new_value, 
                       detected_date, priority_score, id
                FROM change_log
                WHERE detected_date >= ? 
                AND priority_score >= 7
                AND notified = FALSE
                ORDER BY priority_score DESC, detected_date DESC
            """, (since_date,))
            
            changes = [dict(row) for row in cursor.fetchall()]
        
        # Enrich with tender data
        if changes:
            with sqlite3.connect(self.collector.db_path) as tender_conn:
                tender_conn.row_factory = sqlite3.Row
                for change in changes:
                    cursor = tender_conn.execute("""
                        SELECT title, organisation_name, value_high
                        FROM tenders
                        WHERE notice_identifier = ?
                    """, (change['notice_identifier'],))
                    
                    tender_data = cursor.fetchone()
                    if tender_data:
                        change.update(dict(tender_data))
        
        return changes

    def mark_changes_notified(self, change_ids: List[int]):
        """Mark changes as notified"""
        if not change_ids:
            return
            
        placeholders = ','.join('?' * len(change_ids))
        with sqlite3.connect(self.changes_db) as conn:
            conn.execute(f"""
                UPDATE change_log 
                SET notified = TRUE 
                WHERE id IN ({placeholders})
            """, change_ids)

    def get_monitoring_report(self, days: int = 7) -> Dict:
        """Generate comprehensive monitoring report"""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.changes_db) as conn:
            conn.row_factory = sqlite3.Row
            
            # Collection run statistics
            cursor = conn.execute("""
                SELECT COUNT(*) as run_count,
                       AVG(records_collected) as avg_records,
                       AVG(new_records) as avg_new,
                       AVG(run_duration_seconds) as avg_duration
                FROM collection_runs
                WHERE run_date >= ?
            """, (since_date,))
            run_stats = dict(cursor.fetchone())
            
            # Change statistics
            cursor = conn.execute("""
                SELECT change_type, COUNT(*) as count,
                       AVG(priority_score) as avg_priority
                FROM change_log
                WHERE detected_date >= ?
                GROUP BY change_type
                ORDER BY count DESC
            """, (since_date,))
            change_stats = [dict(row) for row in cursor.fetchall()]
            
            # High-priority unnotified changes
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM change_log
                WHERE detected_date >= ?
                AND priority_score >= 8
                AND notified = FALSE
            """, (since_date,))
            urgent_changes = cursor.fetchone()[0]
            
        # Active tender statistics
        with sqlite3.connect(self.collector.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as active_count,
                       COUNT(CASE WHEN value_high >= 100000 THEN 1 END) as high_value_count,
                       MAX(value_high) as max_value
                FROM tenders
                WHERE status = 'Open'
            """)
            tender_stats = dict(cursor.fetchone())
        
        return {
            'reporting_period_days': days,
            'collection_runs': run_stats,
            'change_analysis': change_stats,
            'urgent_changes_pending': urgent_changes,
            'active_tenders': tender_stats,
            'report_generated': datetime.now().isoformat()
        }

    def run_monitoring_cycle(self, keywords: str = "digital transformation") -> Dict:
        """Run complete monitoring cycle with change detection"""
        logger.info("Starting monitoring cycle...")
        
        # Detect changes
        changes = self.detect_changes(keywords)
        
        # Get high-priority changes
        urgent_changes = self.get_high_priority_changes(24)
        
        # Generate summary
        summary = {
            'cycle_timestamp': datetime.now().isoformat(),
            'total_changes': changes['total_changes'],
            'new_opportunities': changes['new_count'],
            'updated_opportunities': changes['updated_count'],
            'urgent_changes': len(urgent_changes),
            'data_changed': changes['data_changed'],
            'urgent_change_details': urgent_changes
        }
        
        logger.info(f"Monitoring cycle complete: {changes['total_changes']} changes detected")
        return summary


if __name__ == "__main__":
    # Initialize monitor
    monitor = TenderMonitor()
    
    # Run monitoring cycle
    results = monitor.run_monitoring_cycle("digital transformation")
    
    # Display results
    print(f"\n=== Monitoring Cycle Results ===")
    print(f"Timestamp: {results['cycle_timestamp']}")
    print(f"Total changes: {results['total_changes']}")
    print(f"New opportunities: {results['new_opportunities']}")
    print(f"Updated opportunities: {results['updated_opportunities']}")
    print(f"Urgent changes: {results['urgent_changes']}")
    print(f"Data changed: {results['data_changed']}")
    
    # Show urgent changes
    if results['urgent_change_details']:
        print(f"\n=== Urgent Changes Requiring Attention ===")
        for change in results['urgent_change_details'][:5]:
            print(f"• {change['title'][:50]}...")
            print(f"  Change: {change['change_type']} (Priority: {change['priority_score']})")
            print(f"  Organization: {change['organisation_name']}")
            if change['old_value'] and change['new_value']:
                print(f"  {change['old_value']} → {change['new_value']}")
            print()
    
    # Generate weekly report
    report = monitor.get_monitoring_report(7)
    print(f"\n=== 7-Day Monitoring Report ===")
    print(f"Collection runs: {report['collection_runs']['run_count']}")
    print(f"Average records per run: {report['collection_runs']['avg_records']:.0f}")
    print(f"Active tenders: {report['active_tenders']['active_count']}")
    print(f"High-value active (£100K+): {report['active_tenders']['high_value_count']}")
    print(f"Highest tender value: £{report['active_tenders']['max_value']:,}" if report['active_tenders']['max_value'] else "No values recorded")