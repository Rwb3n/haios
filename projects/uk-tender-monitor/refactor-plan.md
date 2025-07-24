# UK Tender Monitor - Refactor Plan

**Date Created:** 2025-07-24  
**Purpose:** Establish gold-standard architecture and fix all identified issues  
**Estimated Duration:** 10-12 hours  
**Priority:** High - Required before UAT

## Quick Reference

### 🎯 **Key Fixes**
- [Database Column Fixes](#11-create-alembic-migration-system) - Fix schema misalignment (2 hrs)
- [Service Layer](#phase-2-service-layer-implementation-3-hours) - Implement proper architecture (3 hrs)
- [API Endpoints](#phase-3-api-layer-refactoring-2-hours) - Fix all 9 endpoints (2 hrs)
- [Auto-Classification](#61-implement-auto-classification-hooks) - Enable automation (2 hrs)

### ⏱️ **Time Estimates**
- **Total Duration:** 10-12 hours
- **Day 1:** Database & Services (4 hrs)
- **Day 2:** API & Testing (4 hrs)
- **Day 3:** Integration & Testing (4 hrs)

### ✅ **Critical Path**
1. [Database Schema Fix](#phase-1-database-schema-standardization-2-hours) → 
2. [Service Layer](#phase-2-service-layer-implementation-3-hours) → 
3. [API Refactor](#phase-3-api-layer-refactoring-2-hours) → 
4. [Testing](#phase-5-testing-framework-2-hours)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
   - [System Metrics](#system-metrics)
   - [Critical Issues](#critical-issues)
3. [Refactor Objectives](#refactor-objectives)
   - [Primary Goals](#primary-goals)
   - [Secondary Goals](#secondary-goals)
4. [Architecture Design](#architecture-design)
   - [Layered Architecture](#layered-architecture)
   - [Technology Stack](#technology-stack)
5. [Implementation Plan](#implementation-plan)
   - [Phase 1: Database Schema Standardization](#phase-1-database-schema-standardization-2-hours)
   - [Phase 2: Service Layer Implementation](#phase-2-service-layer-implementation-3-hours)
   - [Phase 3: API Layer Refactoring](#phase-3-api-layer-refactoring-2-hours)
   - [Phase 4: Configuration Management](#phase-4-configuration-management-1-hour)
   - [Phase 5: Testing Framework](#phase-5-testing-framework-2-hours)
   - [Phase 6: Integration Enhancement](#phase-6-integration-enhancement-2-hours)
6. [Testing Strategy](#testing-strategy)
   - [Unit Tests](#unit-tests)
   - [Integration Tests](#integration-tests)
   - [End-to-End Tests](#end-to-end-tests)
7. [Migration Strategy](#migration-strategy)
   - [Pre-Migration Checklist](#pre-migration-checklist)
   - [Migration Steps](#migration-steps)
8. [Risk Mitigation](#risk-mitigation)
   - [Identified Risks](#identified-risks)
   - [Rollback Plan](#rollback-plan)
9. [Success Criteria](#success-criteria)
   - [Must Have](#must-have-core-fixes)
   - [Should Have](#should-have-best-practices)
   - [Nice to Have](#nice-to-have-future)
10. [Timeline](#timeline)
11. [Post-Refactor Benefits](#post-refactor-benefits)
12. [Conclusion](#conclusion)

## Executive Summary

This refactor plan addresses the 44.4% API endpoint failures and establishes consistent architectural patterns throughout the UK Tender Monitor system. The plan focuses on essential fixes while implementing best practices that will support Phase 3 Intelligence Layer development.

## Current State Analysis

### **System Metrics**
- API Endpoints: 55.6% operational (5/9 working)
- Database Schema: Misaligned column names
- Code Patterns: Mixed approaches (dict vs. Pydantic)
- Integration: Manual only (automation not implemented)
- Test Coverage: Unknown (no automated tests)

### **Critical Issues**
1. **Database Schema Misalignment**
   - `classification_timestamp` vs `classification_date`
   - `final_recommendation` vs `recommendation`
   - Missing `filter_passes` column (should be computed)

2. **Code Quality Issues**
   - Inconsistent error handling
   - Mixed validation approaches
   - No dependency injection pattern
   - Hardcoded configuration values

3. **Architectural Gaps**
   - No database migration system
   - Missing service layer abstraction
   - Tight coupling between components
   - No automated testing framework

## Refactor Objectives

### **Primary Goals**
1. ✅ Fix all 4 broken API endpoints (100% operational)
2. ✅ Implement database-first Pydantic models
3. ✅ Establish consistent error handling
4. ✅ Create proper service layer architecture
5. ✅ Add configuration management system

### **Secondary Goals**
1. ⭐ Add comprehensive logging
2. ⭐ Implement dependency injection
3. ⭐ Create automated test suite
4. ⭐ Add API versioning support
5. ⭐ Implement caching layer

## Architecture Design

### **Engineering Style: Pragmatic Clean Architecture with DDD Concepts**

We adopt a pragmatic approach to Clean Architecture that balances theoretical purity with practical development needs. This approach emphasizes:

- **Domain-Driven Design**: Business logic lives in domain models
- **Use Case-Driven**: Services orchestrate specific use cases
- **Dependency Inversion**: Core doesn't depend on infrastructure
- **Explicit Boundaries**: Clear separation between layers
- **Testability First**: Pure functions where possible

### **Directory Structure**

```
src/
├── api/                          # Presentation Layer
│   ├── v1/                       # API Version 1
│   │   ├── endpoints/            # FastAPI routes
│   │   ├── dependencies.py       # Dependency injection
│   │   └── schemas.py            # Request/Response DTOs
│   └── middleware/               # Cross-cutting concerns
│
├── core/                         # Domain Layer (Business Logic)
│   ├── domain/                   # Domain models & entities
│   │   ├── tender.py            # Tender aggregate root
│   │   ├── classification.py    # Classification value object
│   │   └── common/              # Shared domain concepts
│   │       ├── value_objects.py # Money, TenderId, etc.
│   │       └── exceptions.py    # Domain exceptions
│   │
│   ├── services/                 # Application services (use cases)
│   │   ├── classification_service.py
│   │   ├── tender_service.py
│   │   └── monitoring_service.py
│   │
│   └── interfaces/               # Repository & service contracts
│       ├── repositories.py       # Repository protocols
│       └── external_services.py  # External service protocols
│
├── infrastructure/               # Infrastructure Layer
│   ├── database/                 # Data persistence
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── repositories.py      # Repository implementations
│   │   └── migrations/          # Alembic migrations
│   │
│   ├── external/                 # External integrations
│   │   ├── contracts_finder.py  # API client
│   │   └── classification_api.py # ML service client
│   │
│   └── config/                   # Configuration
│       ├── settings.py          # Pydantic settings
│       └── logging.py           # Logging configuration
│
└── tests/                        # Test suite
    ├── unit/                     # Pure unit tests
    ├── integration/              # Integration tests
    └── e2e/                      # End-to-end tests
```

### **Core Design Principles**

#### **1. Domain Models Are Pure**
```python
# core/domain/tender.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .common.value_objects import Money, TenderId, OrganisationId

@dataclass(frozen=True)
class Tender:
    """Tender aggregate root - contains business rules"""
    id: TenderId
    title: str
    description: str
    organisation_id: OrganisationId
    value_range: tuple[Money, Money]
    closing_date: datetime
    status: TenderStatus
    
    def is_eligible_for_classification(self) -> bool:
        """Business rule: Only active tenders can be classified"""
        return (
            self.status == TenderStatus.ACTIVE and
            self.closing_date > datetime.utcnow() and
            self.value_range[1] >= Money(50000, "GBP")
        )
    
    def calculate_priority_score(self) -> int:
        """Pure business logic for priority calculation"""
        base_score = 5
        if self.value_range[1] > Money(1000000, "GBP"):
            base_score += 3
        if self.days_until_closing() < 14:
            base_score += 2
        return min(base_score, 10)
```

#### **2. Services Orchestrate Use Cases**
```python
# core/services/classification_service.py
from typing import Protocol
from ..domain import Tender, Classification
from ..interfaces import TenderRepository, ClassificationRepository

class ClassificationService:
    """Application service orchestrating the classification use case"""
    
    def __init__(
        self,
        tender_repo: TenderRepository,
        classification_repo: ClassificationRepository,
        ml_classifier: MLClassifier
    ):
        self._tender_repo = tender_repo
        self._classification_repo = classification_repo
        self._ml_classifier = ml_classifier
    
    async def classify_tender(self, tender_id: str) -> ClassificationResult:
        """Use case: Classify a tender"""
        # 1. Load aggregate
        tender = await self._tender_repo.get_by_id(TenderId(tender_id))
        if not tender:
            raise TenderNotFoundError(tender_id)
        
        # 2. Check business rules
        if not tender.is_eligible_for_classification():
            raise TenderNotEligibleError(tender_id)
        
        # 3. Perform classification (pure function)
        classification = await self._ml_classifier.classify(tender)
        
        # 4. Apply business logic
        enhanced_classification = self._enhance_with_business_rules(
            tender, classification
        )
        
        # 5. Persist result
        await self._classification_repo.save(enhanced_classification)
        
        return ClassificationResult(
            tender_id=tender.id,
            classification=enhanced_classification
        )
```

#### **3. Repositories as Interfaces**
```python
# core/interfaces/repositories.py
from typing import Protocol, Optional, List
from ..domain import Tender, TenderId, Classification

class TenderRepository(Protocol):
    """Repository interface - implementation details in infrastructure"""
    
    async def get_by_id(self, id: TenderId) -> Optional[Tender]:
        """Load tender aggregate by ID"""
        ...
    
    async def get_unclassified(self, limit: int = 100) -> List[Tender]:
        """Get tenders that haven't been classified"""
        ...
    
    async def save(self, tender: Tender) -> None:
        """Persist tender aggregate"""
        ...
```

#### **4. Explicit Error Handling**
```python
# core/domain/common/exceptions.py
from dataclasses import dataclass

@dataclass(frozen=True)
class DomainError(Exception):
    """Base class for all domain errors"""
    code: str
    message: str
    details: dict = None

class TenderNotFoundError(DomainError):
    def __init__(self, tender_id: str):
        super().__init__(
            code="TENDER_NOT_FOUND",
            message=f"Tender {tender_id} not found",
            details={"tender_id": tender_id}
        )
```

### **Technology Stack**
- **Framework:** FastAPI 0.116.1 (Latest 2025) with full async support
- **ORM:** SQLAlchemy 2.0.41 (Latest 2025) with Alembic migrations
- **Validation:** Pydantic 2.11.7 (Latest 2025) for DTOs, dataclasses for domain
- **Testing:** Pytest 8.4.1 + pytest-asyncio 0.25.0 + pytest-mock
- **Logging:** structlog 25.4.0 for structured logging
- **Config:** Pydantic Settings 2.8.0 with environment support

## Implementation Plan

### **Phase 1: Database Schema Standardization** (2 hours)

#### **1.1 Create Alembic Migration System**
```python
# alembic/versions/001_standardize_schema.py
def upgrade():
    # Rename columns to standard names
    op.alter_column('enhanced_classifications', 
                    'classification_date', 
                    new_column_name='classification_timestamp')
    op.alter_column('enhanced_classifications', 
                    'recommendation', 
                    new_column_name='final_recommendation')
```

#### **1.2 Generate Pydantic Models from Database**
```python
# scripts/generate_models.py
from sqlacodegen import CodeGenerator

# Generate SQLAlchemy models
codegen = CodeGenerator(metadata)
codegen.render()

# Convert to Pydantic models
pydantic_models = convert_to_pydantic(sqlalchemy_models)
```

#### **1.3 Update All Database Queries**
- Replace string SQL with SQLAlchemy queries
- Use consistent column names
- Add proper indexes for performance

### **Phase 2: Domain & Service Layer Implementation** (3 hours)

#### **2.1 Create Domain Models**
```python
# core/domain/tender.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .common.value_objects import Money, TenderId, OrganisationId

@dataclass(frozen=True)
class Tender:
    """Tender aggregate root with business rules"""
    id: TenderId
    title: str
    description: str
    organisation_id: OrganisationId
    value_low: Money
    value_high: Money
    closing_date: datetime
    status: TenderStatus
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Tender':
        """Factory method with validation"""
        return cls(
            id=TenderId(data['notice_identifier']),
            title=data['title'],
            description=data['description'],
            organisation_id=OrganisationId(data['organisation_name']),
            value_low=Money(data.get('value_low', 0), 'GBP'),
            value_high=Money(data.get('value_high', 0), 'GBP'),
            closing_date=datetime.fromisoformat(data['closing_date']),
            status=TenderStatus(data['status'])
        )
    
    def is_high_value(self) -> bool:
        """Business rule: High value tenders > £1M"""
        return self.value_high > Money(1_000_000, 'GBP')

# core/domain/classification.py
@dataclass(frozen=True)
class Classification:
    """Classification value object"""
    tender_id: TenderId
    relevance_score: float
    confidence: float
    recommendation: RecommendationType
    technical_terms: list[str]
    bid_probability: float
    classified_at: datetime
    
    def passes_threshold(self, min_score: float = 60.0) -> bool:
        """Business rule: Minimum score for consideration"""
        return self.relevance_score >= min_score
```

#### **2.2 Implement Application Services**
```python
# core/services/classification_service.py
from typing import List
from ..domain import Tender, Classification
from ..interfaces import TenderRepository, ClassificationRepository, MLClassifier

class ClassificationService:
    """Application service for tender classification use cases"""
    
    def __init__(
        self,
        tender_repo: TenderRepository,
        classification_repo: ClassificationRepository,
        ml_classifier: MLClassifier,
        scorer: RelevanceScorer,
        filter: OpportunityFilter
    ):
        self._tender_repo = tender_repo
        self._classification_repo = classification_repo
        self._ml_classifier = ml_classifier
        self._scorer = scorer
        self._filter = filter
    
    async def classify_single_tender(self, tender_id: str) -> ClassificationResult:
        """Use case: Classify a single tender"""
        # Load domain object
        tender = await self._tender_repo.get_by_id(TenderId(tender_id))
        if not tender:
            raise TenderNotFoundError(tender_id)
        
        # Apply business rules
        if not tender.is_eligible_for_classification():
            raise TenderNotEligibleError(
                f"Tender {tender_id} is not eligible: {tender.status}"
            )
        
        # Execute classification pipeline
        classification = await self._execute_pipeline(tender)
        
        # Persist result
        await self._classification_repo.save(classification)
        
        # Publish domain event
        await self._publish_event(TenderClassifiedEvent(tender.id, classification))
        
        return ClassificationResult.from_domain(tender, classification)
    
    async def classify_unprocessed_tenders(self, limit: int = 50) -> List[ClassificationResult]:
        """Use case: Batch classify unprocessed tenders"""
        unclassified = await self._tender_repo.get_unclassified(limit)
        
        results = []
        for tender in unclassified:
            try:
                result = await self.classify_single_tender(str(tender.id))
                results.append(result)
            except DomainError as e:
                # Log and continue with next tender
                logger.warning(f"Skipping tender {tender.id}: {e}")
        
        return results
    
    async def _execute_pipeline(self, tender: Tender) -> Classification:
        """Execute the classification pipeline"""
        # Step 1: ML Classification
        ml_result = await self._ml_classifier.classify(tender)
        
        # Step 2: Enhanced Scoring
        enhanced_score = await self._scorer.calculate_relevance(tender, ml_result)
        
        # Step 3: Opportunity Filtering
        filter_result = await self._filter.evaluate(tender, enhanced_score)
        
        return Classification(
            tender_id=tender.id,
            relevance_score=enhanced_score.final_score,
            confidence=ml_result.confidence,
            recommendation=filter_result.recommendation,
            technical_terms=ml_result.technical_terms,
            bid_probability=filter_result.bid_probability,
            classified_at=datetime.utcnow()
        )
```

#### **2.3 Implement Repository Infrastructure**
```python
# infrastructure/database/repositories.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List

from core.domain import Tender, TenderId
from core.interfaces import TenderRepository
from .models import TenderModel, ClassificationModel

class SqlAlchemyTenderRepository(TenderRepository):
    """SQLAlchemy implementation of TenderRepository"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, tender_id: TenderId) -> Optional[Tender]:
        query = select(TenderModel).where(
            TenderModel.notice_identifier == str(tender_id)
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        
        return self._to_domain(model) if model else None
    
    async def get_unclassified(self, limit: int = 100) -> List[Tender]:
        query = (
            select(TenderModel)
            .outerjoin(ClassificationModel)
            .where(ClassificationModel.id.is_(None))
            .limit(limit)
        )
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        
        return [self._to_domain(model) for model in models]
    
    def _to_domain(self, model: TenderModel) -> Tender:
        """Convert SQLAlchemy model to domain entity"""
        return Tender(
            id=TenderId(model.notice_identifier),
            title=model.title,
            description=model.description,
            organisation_id=OrganisationId(model.organisation_name),
            value_low=Money(model.value_low or 0, 'GBP'),
            value_high=Money(model.value_high or 0, 'GBP'),
            closing_date=model.closing_date,
            status=TenderStatus(model.status)
        )
```

### **Phase 3: API Layer Refactoring** (2 hours)

#### **3.1 Implement Dependency Injection**
```python
# dependencies.py
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

def get_tender_service(
    session: AsyncSession = Depends(get_db_session)
) -> TenderService:
    repository = TenderRepository(session)
    return TenderService(repository)
```

#### **3.2 Create API DTOs (Data Transfer Objects)**
```python
# api/v1/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class TenderClassificationRequest(BaseModel):
    """Request DTO for tender classification"""
    notice_identifier: str = Field(..., description="Unique tender ID")
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    organisation_name: str
    value_high: int = Field(..., ge=0)
    status: str = Field(..., pattern="^(active|complete|cancelled)$")

class ClassificationResponse(BaseModel):
    """Response DTO for classification result"""
    tender_id: str
    relevance_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    recommendation: str
    technical_terms: List[str]
    bid_probability: float = Field(..., ge=0, le=1)
    classified_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class OpportunityResponse(BaseModel):
    """Response DTO for opportunity listing"""
    tender_id: str
    title: str
    organisation_name: str
    value_range: tuple[int, int]
    closing_date: datetime
    relevance_score: float
    recommendation: str
    priority_level: str
```

#### **3.3 Refactor Endpoints with DDD Error Handling**
```python
# api/v1/endpoints/opportunities.py
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from structlog import get_logger

from core.services import OpportunityService
from core.domain.common.exceptions import DomainError
from ..schemas import OpportunityResponse
from ..dependencies import get_opportunity_service

router = APIRouter(prefix="/opportunities", tags=["opportunities"])
logger = get_logger()

@router.get("/top", response_model=List[OpportunityResponse])
async def get_top_opportunities(
    min_score: float = Query(50.0, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    profile: Optional[str] = Query(None, regex="^(balanced|aggressive|conservative)$"),
    service: OpportunityService = Depends(get_opportunity_service)
):
    """Get top scoring opportunities with optional filtering"""
    try:
        # Call domain service
        opportunities = await service.get_top_opportunities(
            min_score=min_score,
            limit=limit,
            profile=profile
        )
        
        # Map domain objects to DTOs
        return [
            OpportunityResponse(
                tender_id=str(opp.tender.id),
                title=opp.tender.title,
                organisation_name=str(opp.tender.organisation_id),
                value_range=(opp.tender.value_low.amount, opp.tender.value_high.amount),
                closing_date=opp.tender.closing_date,
                relevance_score=opp.classification.relevance_score,
                recommendation=opp.classification.recommendation.value,
                priority_level=opp.priority_level
            )
            for opp in opportunities
        ]
        
    except DomainError as e:
        # Domain errors are client errors
        logger.warning("Domain error in get_top_opportunities", error=e)
        raise HTTPException(status_code=400, detail=e.message)
        
    except Exception as e:
        # Unexpected errors are server errors
        logger.error("Unexpected error in get_top_opportunities", error=e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving opportunities"
        )

# api/v1/endpoints/classification.py
@router.post("/classify", response_model=ClassificationResponse)
async def classify_tender(
    request: TenderClassificationRequest,
    save_to_db: bool = Query(True, description="Save classification to database"),
    service: ClassificationService = Depends(get_classification_service)
):
    """Classify a single tender through the NLP pipeline"""
    try:
        # Map DTO to domain command
        result = await service.classify_single_tender(
            tender_id=request.notice_identifier,
            tender_data=request.dict(),
            persist=save_to_db
        )
        
        # Map domain result to DTO
        return ClassificationResponse(
            tender_id=str(result.tender_id),
            relevance_score=result.classification.relevance_score,
            confidence=result.classification.confidence,
            recommendation=result.classification.recommendation.value,
            technical_terms=result.classification.technical_terms,
            bid_probability=result.classification.bid_probability,
            classified_at=result.classification.classified_at
        )
        
    except TenderNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except TenderNotEligibleError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error("Unexpected error in classify_tender", error=e)
        raise HTTPException(status_code=500, detail="Classification failed")
```

#### **3.3 Implement API Versioning**
```python
# main.py
app = FastAPI(title="UK Tender Monitor API")

# Version 1 routes
app.include_router(
    v1_router,
    prefix="/api/v1",
    tags=["v1"]
)

# Version 2 routes (future)
app.include_router(
    v2_router,
    prefix="/api/v2",
    tags=["v2"]
)
```

### **Phase 4: Configuration Management** (1 hour)

#### **4.1 Create Settings Management**
```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///data/tenders.db"
    database_echo: bool = False
    
    # API
    api_title: str = "UK Tender Monitor"
    api_version: str = "1.0.0"
    cors_origins: List[str] = ["*"]
    
    # Classification
    auto_classification_enabled: bool = True
    classification_interval_minutes: int = 60
    classification_batch_size: int = 10
    
    # Performance
    redis_url: Optional[str] = None
    cache_ttl_seconds: int = 300
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

#### **4.2 Environment-Specific Configs**
```python
# .env.development
DATABASE_URL=sqlite:///data/tenders_dev.db
DATABASE_ECHO=true
AUTO_CLASSIFICATION_ENABLED=true

# .env.production
DATABASE_URL=postgresql://user:pass@host/db
DATABASE_ECHO=false
AUTO_CLASSIFICATION_ENABLED=true
REDIS_URL=redis://localhost:6379
```

### **Phase 5: Testing Framework with DDD Patterns** (2 hours)

#### **5.1 Setup Test Infrastructure**
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from unittest.mock import AsyncMock

from core.interfaces import TenderRepository, ClassificationRepository
from tests.builders import TenderBuilder, ClassificationBuilder

@pytest.fixture
async def client():
    """Test client for API testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_session():
    """In-memory database session for testing"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal(engine) as session:
        yield session

@pytest.fixture
def mock_tender_repository():
    """Mock repository for unit testing"""
    repo = AsyncMock(spec=TenderRepository)
    return repo

@pytest.fixture
def tender_builder():
    """Builder for creating test tenders"""
    return TenderBuilder()
```

#### **5.2 Domain Model Testing**
```python
# tests/unit/domain/test_tender.py
import pytest
from datetime import datetime, timedelta
from core.domain import Tender, TenderStatus
from core.domain.common.value_objects import Money, TenderId

class TestTender:
    """Test tender aggregate business rules"""
    
    def test_tender_eligibility_for_classification(self, tender_builder):
        # Given: An active tender with future closing date
        tender = tender_builder.with_status(TenderStatus.ACTIVE).build()
        
        # Then: It should be eligible
        assert tender.is_eligible_for_classification() is True
    
    def test_closed_tender_not_eligible(self, tender_builder):
        # Given: A closed tender
        tender = tender_builder.with_status(TenderStatus.CLOSED).build()
        
        # Then: It should not be eligible
        assert tender.is_eligible_for_classification() is False
    
    def test_high_value_tender_detection(self, tender_builder):
        # Given: A tender worth £2M
        tender = tender_builder.with_value(Money(2_000_000, 'GBP')).build()
        
        # Then: It should be marked as high value
        assert tender.is_high_value() is True

# tests/builders.py
from datetime import datetime, timedelta
from core.domain import Tender, TenderStatus
from core.domain.common.value_objects import Money, TenderId, OrganisationId

class TenderBuilder:
    """Test data builder for Tender aggregate"""
    
    def __init__(self):
        self._id = TenderId("TEST-001")
        self._title = "Test Tender"
        self._description = "Test Description"
        self._organisation_id = OrganisationId("Test Org")
        self._value_low = Money(50_000, 'GBP')
        self._value_high = Money(100_000, 'GBP')
        self._closing_date = datetime.utcnow() + timedelta(days=30)
        self._status = TenderStatus.ACTIVE
    
    def with_id(self, tender_id: str):
        self._id = TenderId(tender_id)
        return self
    
    def with_status(self, status: TenderStatus):
        self._status = status
        return self
    
    def with_value(self, high_value: Money):
        self._value_high = high_value
        return self
    
    def build(self) -> Tender:
        return Tender(
            id=self._id,
            title=self._title,
            description=self._description,
            organisation_id=self._organisation_id,
            value_low=self._value_low,
            value_high=self._value_high,
            closing_date=self._closing_date,
            status=self._status
        )
```

#### **5.2 Write Core Tests**
```python
# tests/test_api/test_opportunities.py
@pytest.mark.asyncio
async def test_get_top_opportunities(client: AsyncClient, mock_data):
    response = await client.get(
        "/api/v1/opportunities/top",
        params={"min_score": 60, "limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10
    assert all(opp["final_relevance_score"] >= 60 for opp in data)
```

### **Phase 6: Integration Enhancement** (2 hours)

#### **6.1 Implement Auto-Classification Hooks**
```python
# integrations/phase1_integration.py
class EnhancedDataCollector(DataCollector):
    def __init__(self, classification_service: ClassificationService):
        super().__init__()
        self.classification_service = classification_service
    
    async def after_collection_hook(self, new_tender_ids: List[str]):
        """Automatically classify new tenders after collection"""
        if settings.auto_classification_enabled:
            await self.classification_service.classify_batch(new_tender_ids)
```

#### **6.2 Enhance Monitor with Classification Data**
```python
# integrations/enhanced_monitor.py
class EnhancedTenderMonitor(TenderMonitor):
    async def calculate_priority(self, tender: Tender) -> float:
        base_priority = await super().calculate_priority(tender)
        
        # Get classification score
        classification = await self.get_classification(tender.id)
        if classification:
            # Enhance priority with classification score
            enhancement_factor = 1 + (classification.relevance_score / 100)
            return base_priority * enhancement_factor
        
        return base_priority
```

## Testing Strategy

### **Unit Tests**
- All service methods
- Repository queries
- Utility functions
- Model validations

### **Integration Tests**
- API endpoints
- Database operations
- Service interactions
- External API mocking

### **End-to-End Tests**
- Complete workflows
- Data collection → Classification → API
- Error scenarios
- Performance benchmarks

## Migration Strategy

### **Pre-Migration Checklist**
1. ✅ Full database backup
2. ✅ Document current API responses
3. ✅ Note all working endpoints
4. ✅ Export current configurations

### **Migration Steps**
1. **Development Environment**
   - Run all migrations
   - Execute full test suite
   - Verify all endpoints

2. **Staging Environment**
   - Deploy refactored code
   - Run integration tests
   - Performance testing

3. **Production Deployment**
   - Blue-green deployment
   - Monitor error rates
   - Quick rollback ready

## Risk Mitigation

### **Identified Risks**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking working endpoints | High | Medium | Comprehensive testing |
| Data migration failure | High | Low | Backup and rollback plan |
| Performance degradation | Medium | Low | Load testing |
| Integration issues | Medium | Medium | Gradual rollout |

### **Rollback Plan**
1. Keep current codebase tagged
2. Database backup before migration
3. Feature flags for new code
4. Monitor key metrics
5. One-command rollback ready

## Success Criteria

### **Must Have** (Core Fixes)
- ✅ All 9 API endpoints operational
- ✅ Database schema standardized
- ✅ Consistent error handling
- ✅ Configuration management
- ✅ Basic test coverage (>70%)

### **Should Have** (Best Practices)
- ✅ Service layer architecture
- ✅ Dependency injection
- ✅ Automated testing
- ✅ Structured logging
- ✅ API documentation

### **Nice to Have** (Future)
- ⭐ Redis caching
- ⭐ GraphQL API
- ⭐ Real-time updates
- ⭐ Advanced monitoring

## Timeline

### **Day 1** (4 hours)
- Morning: Database schema standardization
- Afternoon: Service layer implementation

### **Day 2** (4 hours)
- Morning: API refactoring
- Afternoon: Testing framework setup

### **Day 3** (4 hours)
- Morning: Integration enhancements
- Afternoon: Testing and documentation

## Post-Refactor Benefits

1. **100% API Functionality**: All endpoints working
2. **Maintainable Code**: Clear architecture patterns
3. **Scalable Design**: Ready for Phase 3
4. **Developer Experience**: Easy to extend
5. **Production Ready**: Proper error handling and logging

## Conclusion

This refactor plan balances essential fixes with architectural improvements. The focus remains on fixing the broken 44.4% of functionality while establishing patterns that will support future development. The 10-12 hour investment will yield a production-ready system suitable for UAT and Phase 3 development.

---
*Refactor Plan prepared for UK Tender Monitor System*  
*Focuses on essential fixes with architectural best practices*