#!/usr/bin/env python3
"""
Setup NocoDB tables for Rhiza Research Mining Agent.
This script creates the required tables with proper schema as defined in the blueprint.
"""

import os
import sys
import json
import httpx
from typing import Dict, Any, List
from datetime import datetime

class NocoDBTableSetup:
    def __init__(self):
        self.api_url = os.getenv('NOCODB_API_URL', 'http://localhost:8081/api/v1')
        self.api_token = os.getenv('NOCODB_API_TOKEN')
        self.project_name = "rhiza_research"
        
        if not self.api_token:
            print("ERROR: NOCODB_API_TOKEN environment variable not set")
            print("Please set it in your .env file or export it")
            sys.exit(1)
            
        self.headers = {
            'xc-token': self.api_token,
            'Content-Type': 'application/json'
        }
        
    def create_project(self) -> str:
        """Create or get the Rhiza Research project."""
        # First, list all projects to check if it exists
        response = httpx.get(
            f"{self.api_url}/db/meta/projects",
            headers=self.headers
        )
        
        if response.status_code == 200:
            projects = response.json().get('list', [])
            for project in projects:
                if project.get('title') == self.project_name:
                    print(f"✓ Project '{self.project_name}' already exists")
                    return project['id']
        
        # Create new project
        create_data = {
            "title": self.project_name,
            "description": "Rhiza Research Mining Agent Data"
        }
        
        response = httpx.post(
            f"{self.api_url}/db/meta/projects",
            headers=self.headers,
            json=create_data
        )
        
        if response.status_code == 200:
            project_id = response.json()['id']
            print(f"✓ Created project '{self.project_name}'")
            return project_id
        else:
            print(f"ERROR creating project: {response.status_code} - {response.text}")
            sys.exit(1)
            
    def get_base_id(self, project_id: str) -> str:
        """Get the base ID for the project."""
        response = httpx.get(
            f"{self.api_url}/db/meta/projects/{project_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            bases = response.json().get('bases', [])
            if bases:
                return bases[0]['id']
        
        print("ERROR: Could not find base ID")
        sys.exit(1)
        
    def create_tables(self, base_id: str):
        """Create all required tables."""
        tables = [
            self._define_raw_research_artifacts_table(),
            self._define_concept_extraction_reports_table(),
            self._define_research_priorities_table(),
            self._define_triage_reports_table()
        ]
        
        for table_def in tables:
            self._create_table(base_id, table_def)
            
    def _create_table(self, base_id: str, table_def: Dict[str, Any]):
        """Create a single table."""
        table_name = table_def['table_name']
        
        # Check if table exists
        response = httpx.get(
            f"{self.api_url}/db/meta/bases/{base_id}/tables",
            headers=self.headers
        )
        
        if response.status_code == 200:
            tables = response.json().get('list', [])
            for table in tables:
                if table.get('table_name') == table_name:
                    print(f"✓ Table '{table_name}' already exists")
                    return
        
        # Create table
        response = httpx.post(
            f"{self.api_url}/db/meta/bases/{base_id}/tables",
            headers=self.headers,
            json=table_def
        )
        
        if response.status_code == 200:
            print(f"✓ Created table '{table_name}'")
        else:
            print(f"ERROR creating table '{table_name}': {response.status_code} - {response.text}")
            
    def _define_raw_research_artifacts_table(self) -> Dict[str, Any]:
        """Define schema for raw_research_artifacts table."""
        return {
            "table_name": "raw_research_artifacts",
            "title": "Raw Research Artifacts",
            "columns": [
                {
                    "column_name": "artifact_id",
                    "title": "Artifact ID",
                    "uidt": "SingleLineText",
                    "pv": True,  # Primary key
                    "rqd": True,  # Required
                    "pk": True,
                    "ai": False,
                    "un": True  # Unique
                },
                {
                    "column_name": "paper_id",
                    "title": "Paper ID",
                    "uidt": "SingleLineText",
                    "rqd": True,
                    "un": True
                },
                {
                    "column_name": "schema_version",
                    "title": "Schema Version",
                    "uidt": "SingleLineText",
                    "cdf": "1.0"  # Default value
                },
                {
                    "column_name": "source_name",
                    "title": "Source Name",
                    "uidt": "SingleLineText",
                    "rqd": True
                },
                {
                    "column_name": "source_url",
                    "title": "Source URL",
                    "uidt": "LongText",
                    "rqd": True
                },
                {
                    "column_name": "source_pdf_url",
                    "title": "Source PDF URL",
                    "uidt": "LongText"
                },
                {
                    "column_name": "title",
                    "title": "Title",
                    "uidt": "LongText",
                    "rqd": True
                },
                {
                    "column_name": "authors",
                    "title": "Authors",
                    "uidt": "JSON",
                    "rqd": True
                },
                {
                    "column_name": "abstract",
                    "title": "Abstract",
                    "uidt": "LongText",
                    "rqd": True
                },
                {
                    "column_name": "categories",
                    "title": "Categories",
                    "uidt": "JSON",
                    "rqd": True
                },
                {
                    "column_name": "full_text",
                    "title": "Full Text",
                    "uidt": "LongText"
                },
                {
                    "column_name": "extracted_sections",
                    "title": "Extracted Sections",
                    "uidt": "JSON"
                },
                {
                    "column_name": "ingestion_timestamp",
                    "title": "Ingestion Timestamp",
                    "uidt": "DateTime",
                    "cdf": "now()"
                },
                {
                    "column_name": "integrity_hash",
                    "title": "Integrity Hash",
                    "uidt": "SingleLineText"
                },
                {
                    "column_name": "trace_id",
                    "title": "Trace ID",
                    "uidt": "SingleLineText"
                },
                {
                    "column_name": "_locked_payload",
                    "title": "Locked Payload",
                    "uidt": "Checkbox",
                    "cdf": True
                }
            ]
        }
        
    def _define_concept_extraction_reports_table(self) -> Dict[str, Any]:
        """Define schema for concept_extraction_reports table."""
        return {
            "table_name": "concept_extraction_reports",
            "title": "Concept Extraction Reports",
            "columns": [
                {
                    "column_name": "report_id",
                    "title": "Report ID",
                    "uidt": "SingleLineText",
                    "pv": True,
                    "rqd": True,
                    "pk": True,
                    "ai": False,
                    "un": True
                },
                {
                    "column_name": "source_artifact_id",
                    "title": "Source Artifact ID",
                    "uidt": "SingleLineText",
                    "rqd": True
                },
                {
                    "column_name": "schema_version",
                    "title": "Schema Version",
                    "uidt": "SingleLineText",
                    "cdf": "1.0"
                },
                {
                    "column_name": "extraction_timestamp",
                    "title": "Extraction Timestamp",
                    "uidt": "DateTime",
                    "cdf": "now()"
                },
                {
                    "column_name": "extraction_method",
                    "title": "Extraction Method",
                    "uidt": "SingleLineText",
                    "rqd": True
                },
                {
                    "column_name": "llm_model",
                    "title": "LLM Model",
                    "uidt": "SingleLineText"
                },
                {
                    "column_name": "concepts",
                    "title": "Concepts",
                    "uidt": "JSON",
                    "rqd": True
                },
                {
                    "column_name": "primary_category",
                    "title": "Primary Category",
                    "uidt": "SingleLineText"
                },
                {
                    "column_name": "keywords",
                    "title": "Keywords",
                    "uidt": "JSON"
                },
                {
                    "column_name": "relevance_tier",
                    "title": "Relevance Tier",
                    "uidt": "Number"
                },
                {
                    "column_name": "impacted_adrs",
                    "title": "Impacted ADRs",
                    "uidt": "JSON"
                },
                {
                    "column_name": "proposed_actions",
                    "title": "Proposed Actions",
                    "uidt": "JSON"
                },
                {
                    "column_name": "trace_id",
                    "title": "Trace ID",
                    "uidt": "SingleLineText"
                },
                {
                    "column_name": "status",
                    "title": "Status",
                    "uidt": "SingleLineText",
                    "cdf": "pending"
                }
            ]
        }
        
    def _define_research_priorities_table(self) -> Dict[str, Any]:
        """Define schema for research_priorities table."""
        return {
            "table_name": "research_priorities",
            "title": "Research Priorities",
            "columns": [
                {
                    "column_name": "priority_id",
                    "title": "Priority ID",
                    "uidt": "SingleLineText",
                    "pv": True,
                    "rqd": True,
                    "pk": True,
                    "ai": False,
                    "un": True
                },
                {
                    "column_name": "generation_counter",
                    "title": "Generation Counter",
                    "uidt": "Number",
                    "rqd": True
                },
                {
                    "column_name": "created_at",
                    "title": "Created At",
                    "uidt": "DateTime",
                    "cdf": "now()"
                },
                {
                    "column_name": "topics",
                    "title": "Topics",
                    "uidt": "JSON",
                    "rqd": True
                },
                {
                    "column_name": "corpus_source",
                    "title": "Corpus Source",
                    "uidt": "SingleLineText"
                },
                {
                    "column_name": "analysis_window",
                    "title": "Analysis Window",
                    "uidt": "SingleLineText"
                },
                {
                    "column_name": "operator_notes",
                    "title": "Operator Notes",
                    "uidt": "LongText"
                }
            ]
        }
        
    def _define_triage_reports_table(self) -> Dict[str, Any]:
        """Define schema for triage_reports table."""
        return {
            "table_name": "triage_reports",
            "title": "Triage Reports",
            "columns": [
                {
                    "column_name": "report_id",
                    "title": "Report ID",
                    "uidt": "SingleLineText",
                    "pv": True,
                    "rqd": True,
                    "pk": True,
                    "ai": False,
                    "un": True
                },
                {
                    "column_name": "topic",
                    "title": "Topic",
                    "uidt": "SingleLineText",
                    "rqd": True
                },
                {
                    "column_name": "generation_counter",
                    "title": "Generation Counter",
                    "uidt": "Number",
                    "rqd": True
                },
                {
                    "column_name": "created_at",
                    "title": "Created At",
                    "uidt": "DateTime",
                    "cdf": "now()"
                },
                {
                    "column_name": "tier_1_papers",
                    "title": "Tier 1 Papers",
                    "uidt": "JSON"
                },
                {
                    "column_name": "tier_2_papers",
                    "title": "Tier 2 Papers",
                    "uidt": "JSON"
                },
                {
                    "column_name": "tier_3_papers",
                    "title": "Tier 3 Papers",
                    "uidt": "JSON"
                },
                {
                    "column_name": "total_papers_analyzed",
                    "title": "Total Papers Analyzed",
                    "uidt": "Number"
                },
                {
                    "column_name": "analysis_criteria",
                    "title": "Analysis Criteria",
                    "uidt": "JSON"
                },
                {
                    "column_name": "operator_selection",
                    "title": "Operator Selection",
                    "uidt": "SingleLineText"
                }
            ]
        }
        
    def run(self):
        """Execute the setup process."""
        print("="*50)
        print("RHIZA NOCODB TABLE SETUP")
        print("="*50)
        print(f"API URL: {self.api_url}")
        print()
        
        try:
            # Create or get project
            project_id = self.create_project()
            
            # Get base ID
            base_id = self.get_base_id(project_id)
            
            # Create tables
            print("\nCreating tables...")
            self.create_tables(base_id)
            
            print("\n✅ Setup completed successfully!")
            print(f"\nProject ID: {project_id}")
            print(f"Base ID: {base_id}")
            print("\nAdd these to your .env file:")
            print(f"NOCODB_PROJECT_ID={project_id}")
            print(f"NOCODB_BASE_ID={base_id}")
            
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    setup = NocoDBTableSetup()
    setup.run()