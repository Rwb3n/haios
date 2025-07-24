# Phase 0: De-Risking & Environment Preparation Plan

**Date Created:** 2025-07-24  
**Purpose:** Eliminate all blockers before starting the main refactor  
**Estimated Duration:** 2-3 hours  
**Priority:** Critical - Must complete before Phase 1

## Executive Summary

Phase 0 ensures we have a stable foundation before beginning the 10-12 hour refactor. This phase focuses on environment setup, dependency verification, quick wins, and creating safety nets. By completing these tasks first, we eliminate the risk of discovering blockers mid-refactor.

## Phase 0 Objectives

1. **Verify Development Environment**: Ensure all tools and dependencies are ready
2. **Create Safety Nets**: Backups, version control, and rollback procedures
3. **Quick Win Fix**: Test column rename fix in isolation
4. **Validate Architecture**: Proof-of-concept for key patterns
5. **Clear the Runway**: Remove any obstacles to smooth refactoring

## Task Breakdown

### **0.1 Environment Verification** (30 minutes)

#### **Python Environment Check**
```bash
# Check Python version (need 3.10+)
python --version

# Create fresh virtual environment
python -m venv venv_refactor
./venv_refactor/Scripts/activate  # Windows
source venv_refactor/bin/activate  # Linux/Mac

# Check current dependencies
pip list
```

#### **Required Dependencies Installation**
```bash
# Core dependencies for refactor (Latest Stable Versions - 2025)
pip install fastapi==0.116.1
pip install sqlalchemy==2.0.41
pip install alembic==1.16.4
pip install pydantic==2.11.7
pip install pydantic-settings==2.8.0
pip install pytest==8.4.1
pip install pytest-asyncio==0.25.0
pip install httpx==0.28.1
pip install structlog==25.4.0

# Save dependency list
pip freeze > requirements-refactor.txt
```

#### **Verification Script**
```python
# verify_environment.py
import sys
print(f"Python: {sys.version}")

try:
    import fastapi
    print(f"✓ FastAPI: {fastapi.__version__}")
except ImportError:
    print("✗ FastAPI not installed")

try:
    import sqlalchemy
    print(f"✓ SQLAlchemy: {sqlalchemy.__version__}")
except ImportError:
    print("✗ SQLAlchemy not installed")

try:
    import alembic
    print(f"✓ Alembic: {alembic.__version__}")
except ImportError:
    print("✗ Alembic not installed")

try:
    import pydantic
    print(f"✓ Pydantic: {pydantic.__version__}")
except ImportError:
    print("✗ Pydantic not installed")
```

### **0.2 Create Safety Nets** (30 minutes)

#### **Database Backup**
```bash
# Create timestamped backup
cp data/tenders.db backups/tenders_$(date +%Y%m%d_%H%M%S).db

# Verify backup
ls -la backups/
sqlite3 backups/tenders_*.db "SELECT COUNT(*) FROM tenders;"
```

#### **Git Safety Branch**
```bash
# Create pre-refactor tag
git add -A
git commit -m "Pre-refactor checkpoint: 55.6% API operational"
git tag -a v1.0-pre-refactor -m "Last stable version before refactor"

# Create refactor branch
git checkout -b refactor/clean-architecture

# Push tag and branch
git push origin v1.0-pre-refactor
git push -u origin refactor/clean-architecture
```

#### **Current State Documentation**
```python
# document_current_state.py
import sqlite3
import json
from datetime import datetime

def document_system_state():
    """Capture current system state for rollback reference"""
    state = {
        "timestamp": datetime.now().isoformat(),
        "api_status": "55.6% operational (5/9 endpoints)",
        "database_stats": {},
        "working_endpoints": [
            "/api/health",
            "/api/info", 
            "/api/classify/single",
            "/api/validation/stats",
            "/api/performance/models"
        ],
        "broken_endpoints": [
            "/api/opportunities/top",
            "/api/opportunities/dashboard-data",
            "/api/performance/system-health",
            "/api/validation/queue"
        ]
    }
    
    # Get database stats
    conn = sqlite3.connect('data/tenders.db')
    state["database_stats"]["total_tenders"] = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
    state["database_stats"]["classified_tenders"] = conn.execute("SELECT COUNT(*) FROM enhanced_classifications").fetchone()[0]
    conn.close()
    
    # Save state
    with open('backups/system_state_pre_refactor.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    print("System state documented")

document_system_state()
```

### **0.3 Quick Win Column Fix Test** (45 minutes)

#### **Isolated Fix Test**
```python
# test_column_fix.py
"""Test the column fix in isolation before full refactor"""
import sqlite3
import shutil

# Work on a copy
shutil.copy('data/tenders.db', 'data/tenders_test.db')

conn = sqlite3.connect('data/tenders_test.db')
cursor = conn.cursor()

# Check current schema
cursor.execute("PRAGMA table_info(enhanced_classifications)")
columns = cursor.fetchall()
print("Current columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Test the fix approach
try:
    # Option 1: Rename columns (for new Alembic migration)
    cursor.execute("""
        ALTER TABLE enhanced_classifications 
        RENAME COLUMN classification_date TO classification_timestamp
    """)
    print("✓ Column rename successful")
except Exception as e:
    print(f"✗ Column rename failed: {e}")
    
    # Option 2: Create view (immediate fix)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_enhanced_classifications AS
        SELECT 
            *,
            classification_date as classification_timestamp,
            recommendation as final_recommendation
        FROM enhanced_classifications
    """)
    print("✓ Compatibility view created")

# Test a problematic query
try:
    cursor.execute("""
        SELECT notice_identifier, classification_timestamp, final_recommendation
        FROM v_enhanced_classifications
        LIMIT 1
    """)
    result = cursor.fetchone()
    print(f"✓ Query successful: {result}")
except Exception as e:
    print(f"✗ Query failed: {e}")

conn.close()
```

#### **API Quick Fix Validation**
```python
# validate_api_fix.py
"""Validate that column fixes will resolve API issues"""
import requests
import json

# Test currently broken endpoint
response = requests.get("http://localhost:8000/api/opportunities/top?min_score=50&limit=5")
print(f"Current status: {response.status_code}")
if response.status_code == 500:
    print("Error details:", response.json().get('detail', 'No details'))

# Document exact error for fix validation
with open('backups/api_errors_pre_fix.json', 'w') as f:
    json.dump({
        "endpoint": "/api/opportunities/top",
        "status": response.status_code,
        "error": response.text
    }, f, indent=2)
```

### **0.4 Architecture Proof of Concept** (30 minutes)

#### **DDD Pattern Validation**
```python
# poc_ddd_pattern.py
"""Validate our DDD approach with a minimal example"""
from dataclasses import dataclass
from typing import Protocol, Optional
from datetime import datetime

# Domain Layer
@dataclass(frozen=True)
class TenderId:
    value: str
    
    def __str__(self):
        return self.value

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
    
    def __gt__(self, other):
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount > other.amount

@dataclass(frozen=True)
class Tender:
    id: TenderId
    title: str
    value: Money
    
    def is_high_value(self) -> bool:
        return self.value > Money(1_000_000, 'GBP')

# Repository Interface
class TenderRepository(Protocol):
    async def get_by_id(self, tender_id: TenderId) -> Optional[Tender]:
        ...

# Service Layer
class TenderService:
    def __init__(self, repository: TenderRepository):
        self._repository = repository
    
    async def get_tender_details(self, tender_id: str) -> Optional[Tender]:
        return await self._repository.get_by_id(TenderId(tender_id))

# Test the pattern
tender = Tender(
    id=TenderId("TEST-001"),
    title="Test Tender",
    value=Money(2_000_000, 'GBP')
)

print(f"Tender {tender.id} is high value: {tender.is_high_value()}")
print("✓ DDD pattern validated")
```

#### **Async Pattern Test**
```python
# poc_async_pattern.py
"""Validate async patterns work correctly"""
import asyncio
from typing import List

async def mock_database_call(id: str) -> dict:
    """Simulate async database call"""
    await asyncio.sleep(0.1)  # Simulate I/O
    return {"id": id, "title": f"Tender {id}"}

async def batch_process(ids: List[str]) -> List[dict]:
    """Test concurrent processing"""
    tasks = [mock_database_call(id) for id in ids]
    return await asyncio.gather(*tasks)

# Test async execution
async def main():
    ids = ["TEST-001", "TEST-002", "TEST-003"]
    results = await batch_process(ids)
    print(f"✓ Async pattern works: {len(results)} results")

asyncio.run(main())
```

### **0.5 Runway Clearing** (15 minutes)

#### **Stop Running Services**
```bash
# Kill any running API servers
# Windows
tasklist | findstr python
taskkill /F /PID <pid>

# Linux/Mac
ps aux | grep python
kill -9 <pid>

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

#### **Create Work Directories**
```bash
# Create refactor structure
mkdir -p src/api/v1/endpoints
mkdir -p src/api/v1/schemas
mkdir -p src/core/domain/common
mkdir -p src/core/services
mkdir -p src/core/interfaces
mkdir -p src/infrastructure/database/migrations
mkdir -p src/infrastructure/config
mkdir -p tests/unit/domain
mkdir -p tests/integration
mkdir -p tests/e2e
mkdir -p backups

# Create __init__.py files
touch src/__init__.py
touch src/api/__init__.py
touch src/core/__init__.py
touch src/infrastructure/__init__.py
```

#### **Final Checklist Script**
```python
# phase0_final_check.py
"""Final verification before starting refactor"""
import os
import subprocess
import sys

checks = []

# Check Git status
git_status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
checks.append(("Git working directory clean", len(git_status.stdout) == 0))

# Check backup exists
backup_exists = any('tenders_' in f for f in os.listdir('backups'))
checks.append(("Database backup created", backup_exists))

# Check dependencies
try:
    import fastapi
    import sqlalchemy
    import alembic
    checks.append(("Required packages installed", True))
except ImportError:
    checks.append(("Required packages installed", False))

# Check API not running
try:
    import requests
    requests.get("http://localhost:8000", timeout=1)
    checks.append(("API server stopped", False))
except:
    checks.append(("API server stopped", True))

# Print results
print("\n=== PHASE 0 FINAL CHECKLIST ===")
all_passed = True
for check, passed in checks:
    status = "✓" if passed else "✗"
    print(f"{status} {check}")
    if not passed:
        all_passed = False

if all_passed:
    print("\n✅ ALL CHECKS PASSED - Ready for Phase 1!")
else:
    print("\n❌ SOME CHECKS FAILED - Please fix before proceeding")
    sys.exit(1)
```

## Phase 0 Deliverables

1. **Environment Ready**: All dependencies installed and verified
2. **Safety Nets**: Database backed up, Git tagged, state documented
3. **Quick Fix Tested**: Column rename approach validated
4. **Architecture Validated**: DDD patterns proven to work
5. **Runway Clear**: No blockers for main refactor

## Success Criteria

- ✅ All dependencies installed with correct versions
- ✅ Database backup completed and verified
- ✅ Git pre-refactor tag created
- ✅ Column fix approach tested successfully
- ✅ DDD pattern POC runs without errors
- ✅ Work directories created
- ✅ Final checklist shows all green

## Time Investment

**Total: 2-3 hours**
- Environment setup: 30 minutes
- Safety nets: 30 minutes  
- Quick fix test: 45 minutes
- Architecture POC: 30 minutes
- Runway clearing: 15 minutes
- Buffer time: 30-60 minutes

## Next Steps

Once Phase 0 is complete:
1. Review all test results
2. Confirm no blockers remain
3. Begin Phase 1: Database Schema Standardization
4. Follow the main refactor plan

---
*Phase 0 De-risking Plan - UK Tender Monitor System*  
*Eliminate all blockers before beginning the main refactor*