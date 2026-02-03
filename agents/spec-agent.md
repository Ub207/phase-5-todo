# Spec Agent (Specification Analyzer)

**Version**: 1.0.0
**Created**: 2026-02-02
**Branch**: 001-fuel-consumption-pwa
**Status**: Active

---

## Purpose

The Spec Agent analyzes advanced feature specifications for the Todo App and generates structured implementation plans. It identifies features, dependencies, and creates actionable task lists for Phase 5 development.

**Core Responsibilities:**
- Parse specifications from `/specs` folder
- Identify advanced features (Recurring tasks, Reminders, Tags, Filters, etc.)
- Map dependencies (Kafka topics, Dapr components, Database schemas)
- Generate structured task lists with priority ordering
- Create dependency graphs for implementation planning

---

## Agent Context

### Surface
Operates at the **specification analysis** level, bridging requirements and implementation planning.

### Success Criteria
- All specs are parsed accurately with no data loss
- Feature list is complete and categorized
- Dependencies are explicitly mapped with ownership
- Task lists are actionable, testable, and dependency-ordered
- Output artifacts follow SDD-RI standards

---

## Input/Output Contract

### Inputs

1. **Project Specifications** (Primary)
   - Location: `/specs/<feature-name>/spec.md`
   - Format: Markdown with structured sections
   - Content: Feature descriptions, requirements, acceptance criteria

2. **Existing Codebase Context** (Secondary)
   - Location: `../todo_phase3/backend/`, `../todo_phase3/frontend/`
   - Purpose: Understanding current implementation patterns

3. **Configuration Files** (Optional)
   - `.env.example` - Environment variables and integrations
   - `requirements.txt` - Python dependencies
   - `package.json` - Node.js dependencies

### Outputs

1. **Feature Analysis Report**
   - Location: `specs/<feature-name>/analysis.md`
   - Content:
     - Feature breakdown by category
     - Complexity assessment
     - Integration points
     - Risk factors

2. **Dependency Map**
   - Location: `specs/<feature-name>/dependencies.json`
   - Structure:
     ```json
     {
       "features": {
         "recurring-tasks": {
           "kafka_topics": ["task.created", "task.scheduled"],
           "dapr_components": ["statestore", "pubsub"],
           "db_tables": ["recurring_patterns", "task_instances"],
           "external_apis": ["calendar-service"],
           "frontend_components": ["RecurringTaskForm", "ScheduleView"]
         }
       },
       "shared_dependencies": {
         "kafka": ["zookeeper", "broker"],
         "dapr": ["redis", "kafka-pubsub"]
       }
     }
     ```

3. **Implementation Task List**
   - Location: `specs/<feature-name>/tasks.md`
   - Format: SDD-RI compliant tasks.md
   - Content: Dependency-ordered, testable tasks

4. **Architecture Decision Prompts**
   - Suggestions for ADRs when significant decisions are detected
   - Format: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`"

---

## Feature Categories

### Phase 5 Advanced Features

1. **Recurring Tasks**
   - Pattern-based scheduling (daily, weekly, monthly, custom)
   - Instance generation and management
   - Skip/postpone handling
   - Dependencies: Kafka (scheduling events), Dapr (state management)

2. **Reminders & Notifications**
   - Time-based reminders
   - Location-based triggers (if applicable)
   - Multi-channel delivery (email, push, in-app)
   - Dependencies: Kafka (notification events), External notification service

3. **Tags & Categories**
   - Hierarchical tag system
   - Tag-based filtering and search
   - Tag analytics
   - Dependencies: Database (tags table, task_tags junction)

4. **Advanced Filters**
   - Complex query builder
   - Saved filter presets
   - Filter sharing
   - Dependencies: ElasticSearch (optional), Database indexes

5. **Event Streaming (Kafka)**
   - Task lifecycle events
   - Cross-service communication
   - Event replay capability
   - Dependencies: Kafka cluster, Schema registry

6. **Dapr Integration**
   - State management
   - Pub/Sub messaging
   - Service invocation
   - Dependencies: Dapr runtime, Redis sidecar

---

## Dependencies Identification Framework

### Dependency Types

1. **Infrastructure Dependencies**
   - Kafka cluster (Zookeeper + Brokers)
   - Dapr runtime + sidecars
   - Redis (for Dapr state store)
   - PostgreSQL (existing DB + migrations)

2. **Service Dependencies**
   - Backend API (FastAPI)
   - Frontend (Next.js)
   - MCP Server (existing)
   - Notification service (new)

3. **Data Dependencies**
   - Database schemas (new tables, columns)
   - Kafka topics (event schemas)
   - State store schemas (Dapr)
   - Migration scripts

4. **External Dependencies**
   - Email service (SendGrid/SMTP)
   - Push notification service (Firebase/OneSignal)
   - Calendar integration (Google Calendar API - optional)

---

## Analysis Workflow

### Phase 1: Specification Parsing

**Input**: Raw spec files from `/specs/<feature-name>/spec.md`

**Process**:
1. Extract feature name and description
2. Identify acceptance criteria
3. Parse user stories
4. Extract non-functional requirements
5. Identify constraints and assumptions

**Output**: Structured feature object

**Tools**:
- Markdown parser
- YAML front-matter extractor
- Regex patterns for structured sections

---

### Phase 2: Dependency Extraction

**Input**: Parsed feature object

**Process**:
1. **Scan for Keywords**:
   - "Kafka", "event", "stream", "publish", "subscribe"
   - "Dapr", "state", "pubsub", "sidecar"
   - "database", "table", "schema", "migration"
   - "API", "endpoint", "service"
   - "notification", "email", "push"

2. **Map to Dependency Types**:
   - Infrastructure: Kafka, Dapr, Redis, PostgreSQL
   - Services: Backend, Frontend, MCP
   - Data: Tables, Topics, Schemas
   - External: Third-party APIs

3. **Identify Cross-Feature Dependencies**:
   - Shared Kafka topics
   - Shared Dapr components
   - Shared database tables

**Output**: Dependency map (JSON)

---

### Phase 3: Task Generation

**Input**: Feature object + Dependency map

**Process**:
1. **Break Down Features**:
   - Infrastructure setup tasks
   - Backend implementation tasks
   - Frontend implementation tasks
   - Integration tasks
   - Testing tasks

2. **Order by Dependency**:
   - Level 0: Infrastructure (Kafka, Dapr, Redis)
   - Level 1: Database migrations
   - Level 2: Backend services
   - Level 3: Frontend components
   - Level 4: Integration & E2E tests

3. **Add Test Cases**:
   - Unit tests (per component)
   - Integration tests (service boundaries)
   - E2E tests (user flows)

**Output**: `tasks.md` following SDD-RI format

---

### Phase 4: Risk & ADR Identification

**Input**: Feature object + Dependency map + Tasks

**Process**:
1. **Risk Assessment**:
   - Complexity score (1-10)
   - Dependency count
   - External integration risk
   - Data migration risk

2. **ADR Detection** (Three-part test):
   - **Impact**: Long-term consequences? (framework, data model, API)
   - **Alternatives**: Multiple viable options?
   - **Scope**: Cross-cutting system influence?

   If ALL true → Suggest ADR

**Output**: Risk summary + ADR suggestions

---

## Implementation Guide

### Step 1: Setup

```bash
# Create specs directory structure
mkdir -p specs/{recurring-tasks,reminders,tags,filters,kafka-events,dapr-components}

# Initialize spec templates
for feature in recurring-tasks reminders tags filters kafka-events dapr-components; do
  cp .specify/templates/spec-template.md specs/$feature/spec.md
done
```

### Step 2: Run Spec Agent

```bash
# Analyze all specs
python agents/spec_agent.py --input specs/ --output specs/

# Analyze specific feature
python agents/spec_agent.py --feature recurring-tasks
```

### Step 3: Review Outputs

```bash
# Check feature analysis
cat specs/recurring-tasks/analysis.md

# Review dependencies
cat specs/recurring-tasks/dependencies.json

# Check generated tasks
cat specs/recurring-tasks/tasks.md
```

### Step 4: Create ADRs (if prompted)

```bash
# Example ADR prompt:
# 📋 Architectural decision detected: Kafka topic schema design for task events
# Document? Run `/sp.adr kafka-task-event-schema`

# Create ADR
/sp.adr kafka-task-event-schema
```

---

## Agent Script (Python Implementation)

### File: `agents/spec_agent.py`

```python
#!/usr/bin/env python3
"""
Spec Agent - Specification Analyzer for Todo App Phase 5
Parses specs, identifies dependencies, generates structured plans.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass, asdict
import yaml


@dataclass
class Feature:
    """Represents a parsed feature specification."""
    name: str
    description: str
    category: str
    acceptance_criteria: List[str]
    complexity: int  # 1-10
    priority: str  # high, medium, low
    dependencies: List[str]
    kafka_topics: List[str]
    dapr_components: List[str]
    db_tables: List[str]
    api_endpoints: List[str]
    frontend_components: List[str]


@dataclass
class DependencyMap:
    """Maps all dependencies across features."""
    features: Dict[str, Dict[str, List[str]]]
    shared_infrastructure: Dict[str, List[str]]
    external_services: List[str]


class SpecParser:
    """Parses specification markdown files."""

    def __init__(self, spec_path: Path):
        self.spec_path = spec_path
        self.content = spec_path.read_text(encoding='utf-8')

    def extract_front_matter(self) -> Dict[str, Any]:
        """Extract YAML front matter from spec."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', self.content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))
        return {}

    def extract_section(self, heading: str) -> str:
        """Extract content under a specific heading."""
        pattern = rf'^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)'
        match = re.search(pattern, self.content, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def extract_acceptance_criteria(self) -> List[str]:
        """Extract acceptance criteria from spec."""
        section = self.extract_section("Acceptance Criteria")
        criteria = re.findall(r'^\s*[-*]\s+(.+)$', section, re.MULTILINE)
        return criteria

    def identify_kafka_topics(self) -> List[str]:
        """Identify Kafka topics mentioned in spec."""
        topics = re.findall(r'topic[:\s]+["`]?([\w\.-]+)["`]?', self.content, re.IGNORECASE)
        return list(set(topics))

    def identify_dapr_components(self) -> List[str]:
        """Identify Dapr components mentioned in spec."""
        components = []
        keywords = {
            'state': 'statestore',
            'pubsub': 'pubsub',
            'binding': 'bindings',
            'secret': 'secretstore'
        }
        for keyword, component in keywords.items():
            if re.search(rf'\b{keyword}\b', self.content, re.IGNORECASE):
                components.append(component)
        return list(set(components))

    def identify_db_tables(self) -> List[str]:
        """Identify database tables mentioned in spec."""
        tables = re.findall(r'table[:\s]+["`]?([\w_]+)["`]?', self.content, re.IGNORECASE)
        return list(set(tables))

    def identify_api_endpoints(self) -> List[str]:
        """Identify API endpoints mentioned in spec."""
        endpoints = re.findall(r'(?:GET|POST|PUT|DELETE|PATCH)\s+(/[\w/-]+)', self.content)
        return list(set(endpoints))

    def identify_frontend_components(self) -> List[str]:
        """Identify frontend components mentioned in spec."""
        components = re.findall(r'component[:\s]+["`]?([\w]+)["`]?', self.content, re.IGNORECASE)
        return list(set(components))

    def assess_complexity(self) -> int:
        """Assess feature complexity (1-10)."""
        score = 5  # baseline

        # Adjust based on various factors
        if 'kafka' in self.content.lower():
            score += 1
        if 'dapr' in self.content.lower():
            score += 1
        if len(self.identify_db_tables()) > 2:
            score += 1
        if 'migration' in self.content.lower():
            score += 1
        if 'external' in self.content.lower() or 'third-party' in self.content.lower():
            score += 1

        return min(score, 10)

    def parse(self) -> Feature:
        """Parse spec file into Feature object."""
        front_matter = self.extract_front_matter()

        return Feature(
            name=front_matter.get('name', self.spec_path.stem),
            description=self.extract_section("Description") or self.extract_section("Overview"),
            category=front_matter.get('category', 'general'),
            acceptance_criteria=self.extract_acceptance_criteria(),
            complexity=self.assess_complexity(),
            priority=front_matter.get('priority', 'medium'),
            dependencies=front_matter.get('dependencies', []),
            kafka_topics=self.identify_kafka_topics(),
            dapr_components=self.identify_dapr_components(),
            db_tables=self.identify_db_tables(),
            api_endpoints=self.identify_api_endpoints(),
            frontend_components=self.identify_frontend_components()
        )


class DependencyAnalyzer:
    """Analyzes dependencies across features."""

    def __init__(self, features: List[Feature]):
        self.features = features

    def build_dependency_map(self) -> DependencyMap:
        """Build comprehensive dependency map."""
        feature_deps = {}
        shared_infra = {
            'kafka': [],
            'dapr': [],
            'database': [],
            'redis': []
        }
        external = set()

        for feature in self.features:
            feature_deps[feature.name] = {
                'kafka_topics': feature.kafka_topics,
                'dapr_components': feature.dapr_components,
                'db_tables': feature.db_tables,
                'api_endpoints': feature.api_endpoints,
                'frontend_components': feature.frontend_components
            }

            # Aggregate shared infrastructure
            shared_infra['kafka'].extend(feature.kafka_topics)
            shared_infra['dapr'].extend(feature.dapr_components)
            shared_infra['database'].extend(feature.db_tables)

            # Check for Redis usage (common with Dapr)
            if feature.dapr_components:
                shared_infra['redis'].append(f"{feature.name}-redis")

        # Deduplicate shared infra
        for key in shared_infra:
            shared_infra[key] = list(set(shared_infra[key]))

        return DependencyMap(
            features=feature_deps,
            shared_infrastructure=shared_infra,
            external_services=list(external)
        )

    def identify_shared_resources(self) -> Dict[str, List[str]]:
        """Identify resources shared across multiple features."""
        shared = {}

        # Check Kafka topics
        topic_usage = {}
        for feature in self.features:
            for topic in feature.kafka_topics:
                topic_usage.setdefault(topic, []).append(feature.name)

        shared['kafka_topics'] = {
            topic: features
            for topic, features in topic_usage.items()
            if len(features) > 1
        }

        # Check DB tables
        table_usage = {}
        for feature in self.features:
            for table in feature.db_tables:
                table_usage.setdefault(table, []).append(feature.name)

        shared['db_tables'] = {
            table: features
            for table, features in table_usage.items()
            if len(features) > 1
        }

        return shared


class TaskGenerator:
    """Generates implementation tasks from features."""

    def __init__(self, feature: Feature, dependency_map: DependencyMap):
        self.feature = feature
        self.dependency_map = dependency_map

    def generate_tasks_md(self) -> str:
        """Generate tasks.md following SDD-RI format."""
        tasks = []
        task_id = 1

        # Infrastructure tasks
        if self.feature.kafka_topics:
            tasks.append(self._create_task(
                task_id, "Setup Kafka Topics",
                f"Create Kafka topics: {', '.join(self.feature.kafka_topics)}",
                ["kafka-admin"],
                ["Verify topic creation", "Check partition count", "Validate retention policy"]
            ))
            task_id += 1

        if self.feature.dapr_components:
            tasks.append(self._create_task(
                task_id, "Configure Dapr Components",
                f"Setup Dapr components: {', '.join(self.feature.dapr_components)}",
                [task_id - 1] if self.feature.kafka_topics else [],
                ["Verify component registration", "Test component connectivity"]
            ))
            task_id += 1

        # Database tasks
        if self.feature.db_tables:
            tasks.append(self._create_task(
                task_id, "Create Database Migrations",
                f"Add tables: {', '.join(self.feature.db_tables)}",
                [],
                ["Run migration", "Verify schema", "Test rollback"]
            ))
            task_id += 1

        # Backend tasks
        if self.feature.api_endpoints:
            tasks.append(self._create_task(
                task_id, "Implement Backend API",
                f"Add endpoints: {', '.join(self.feature.api_endpoints)}",
                [task_id - 1] if self.feature.db_tables else [],
                ["Write unit tests", "Test API endpoints", "Validate responses"]
            ))
            task_id += 1

        # Frontend tasks
        if self.feature.frontend_components:
            tasks.append(self._create_task(
                task_id, "Implement Frontend Components",
                f"Create components: {', '.join(self.feature.frontend_components)}",
                [task_id - 1] if self.feature.api_endpoints else [],
                ["Write component tests", "Test UI interactions", "Verify responsiveness"]
            ))
            task_id += 1

        # Integration tests
        tasks.append(self._create_task(
            task_id, "End-to-End Testing",
            f"Test complete {self.feature.name} workflow",
            [i for i in range(1, task_id)],
            ["Write E2E tests", "Test all user flows", "Verify error handling"]
        ))

        return self._format_tasks_md(tasks)

    def _create_task(self, task_id: int, title: str, description: str,
                     depends_on: List[int], acceptance: List[str]) -> Dict:
        """Create a task dictionary."""
        return {
            'id': task_id,
            'title': title,
            'description': description,
            'depends_on': depends_on,
            'acceptance_criteria': acceptance,
            'status': 'pending'
        }

    def _format_tasks_md(self, tasks: List[Dict]) -> str:
        """Format tasks as markdown."""
        md = f"# Tasks: {self.feature.name}\n\n"
        md += f"**Feature**: {self.feature.name}\n"
        md += f"**Priority**: {self.feature.priority}\n"
        md += f"**Complexity**: {self.feature.complexity}/10\n\n"
        md += "---\n\n"

        for task in tasks:
            md += f"## Task {task['id']}: {task['title']}\n\n"
            md += f"**Description**: {task['description']}\n\n"

            if task['depends_on']:
                md += f"**Depends on**: {', '.join(map(str, task['depends_on']))}\n\n"

            md += "**Acceptance Criteria**:\n"
            for criterion in task['acceptance_criteria']:
                md += f"- [ ] {criterion}\n"

            md += f"\n**Status**: {task['status']}\n\n"
            md += "---\n\n"

        return md


class SpecAgent:
    """Main Spec Agent orchestrator."""

    def __init__(self, specs_dir: Path, output_dir: Path = None):
        self.specs_dir = specs_dir
        self.output_dir = output_dir or specs_dir
        self.features: List[Feature] = []

    def analyze_all_specs(self):
        """Analyze all spec files in specs directory."""
        spec_files = list(self.specs_dir.rglob("spec.md"))

        print(f"Found {len(spec_files)} spec files")

        for spec_file in spec_files:
            print(f"\nAnalyzing: {spec_file}")
            parser = SpecParser(spec_file)
            feature = parser.parse()
            self.features.append(feature)

            # Generate outputs
            self._generate_analysis(feature, spec_file.parent)
            self._generate_tasks(feature, spec_file.parent)

    def analyze_feature(self, feature_name: str):
        """Analyze a specific feature."""
        spec_file = self.specs_dir / feature_name / "spec.md"

        if not spec_file.exists():
            print(f"Error: Spec file not found: {spec_file}")
            return

        print(f"Analyzing: {spec_file}")
        parser = SpecParser(spec_file)
        feature = parser.parse()
        self.features.append(feature)

        # Generate outputs
        self._generate_analysis(feature, spec_file.parent)
        self._generate_tasks(feature, spec_file.parent)

        # Generate dependency map for this feature
        analyzer = DependencyAnalyzer([feature])
        dep_map = analyzer.build_dependency_map()
        self._save_dependency_map(dep_map, spec_file.parent)

    def generate_dependency_map(self):
        """Generate comprehensive dependency map."""
        analyzer = DependencyAnalyzer(self.features)
        dep_map = analyzer.build_dependency_map()
        shared = analyzer.identify_shared_resources()

        # Save to root specs directory
        self._save_dependency_map(dep_map, self.specs_dir)

        # Save shared resources report
        shared_file = self.output_dir / "shared-resources.json"
        shared_file.write_text(json.dumps(shared, indent=2))
        print(f"\nShared resources saved to: {shared_file}")

    def _generate_analysis(self, feature: Feature, output_dir: Path):
        """Generate feature analysis report."""
        analysis = f"""# Feature Analysis: {feature.name}

**Category**: {feature.category}
**Priority**: {feature.priority}
**Complexity**: {feature.complexity}/10

## Description

{feature.description}

## Acceptance Criteria

{chr(10).join(f"- {criterion}" for criterion in feature.acceptance_criteria)}

## Dependencies

### Infrastructure
- **Kafka Topics**: {', '.join(feature.kafka_topics) or 'None'}
- **Dapr Components**: {', '.join(feature.dapr_components) or 'None'}
- **Database Tables**: {', '.join(feature.db_tables) or 'None'}

### API
- **Endpoints**: {chr(10).join(f"  - {ep}" for ep in feature.api_endpoints) or 'None'}

### Frontend
- **Components**: {', '.join(feature.frontend_components) or 'None'}

## Risk Assessment

**Complexity Score**: {feature.complexity}/10

**Risk Factors**:
- Infrastructure Dependencies: {'High' if len(feature.kafka_topics) + len(feature.dapr_components) > 2 else 'Medium' if len(feature.kafka_topics) + len(feature.dapr_components) > 0 else 'Low'}
- Database Changes: {'High' if len(feature.db_tables) > 2 else 'Medium' if len(feature.db_tables) > 0 else 'Low'}
- External Integrations: {'Pending assessment'}

## Recommendations

{self._generate_recommendations(feature)}
"""

        analysis_file = output_dir / "analysis.md"
        analysis_file.write_text(analysis)
        print(f"Analysis saved to: {analysis_file}")

    def _generate_recommendations(self, feature: Feature) -> str:
        """Generate recommendations based on feature analysis."""
        recommendations = []

        if feature.complexity > 7:
            recommendations.append("- Consider breaking this feature into smaller sub-features")

        if feature.kafka_topics:
            recommendations.append("- 📋 **ADR Needed**: Kafka topic schema design and versioning strategy")

        if feature.dapr_components:
            recommendations.append("- 📋 **ADR Needed**: Dapr component configuration and state management approach")

        if len(feature.db_tables) > 2:
            recommendations.append("- Plan database migration strategy carefully")
            recommendations.append("- Consider performance impact of new tables")

        return '\n'.join(recommendations) or "- No specific recommendations"

    def _generate_tasks(self, feature: Feature, output_dir: Path):
        """Generate tasks.md for feature."""
        # Build minimal dependency map for this feature
        analyzer = DependencyAnalyzer([feature])
        dep_map = analyzer.build_dependency_map()

        generator = TaskGenerator(feature, dep_map)
        tasks_md = generator.generate_tasks_md()

        tasks_file = output_dir / "tasks.md"
        tasks_file.write_text(tasks_md)
        print(f"Tasks saved to: {tasks_file}")

    def _save_dependency_map(self, dep_map: DependencyMap, output_dir: Path):
        """Save dependency map as JSON."""
        dep_file = output_dir / "dependencies.json"
        dep_file.write_text(json.dumps(asdict(dep_map), indent=2))
        print(f"Dependencies saved to: {dep_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Spec Agent - Analyze Todo App specifications")
    parser.add_argument('--input', type=Path, default=Path('specs'),
                       help='Input specs directory')
    parser.add_argument('--output', type=Path, default=None,
                       help='Output directory (defaults to input)')
    parser.add_argument('--feature', type=str, default=None,
                       help='Analyze specific feature only')

    args = parser.parse_args()

    agent = SpecAgent(args.input, args.output)

    if args.feature:
        agent.analyze_feature(args.feature)
    else:
        agent.analyze_all_specs()
        agent.generate_dependency_map()

    print("\n✅ Spec analysis complete!")
    print("\nNext steps:")
    print("1. Review generated analysis.md files")
    print("2. Check dependencies.json for infrastructure requirements")
    print("3. Review tasks.md files")
    print("4. Create ADRs for suggested architectural decisions")


if __name__ == '__main__':
    main()
```

---

## Example Usage

### Scenario 1: Analyze All Specs

```bash
# Run spec agent on all specs
python agents/spec_agent.py --input specs/

# Review outputs
ls -R specs/
# specs/
# ├── recurring-tasks/
# │   ├── spec.md
# │   ├── analysis.md
# │   ├── tasks.md
# │   └── dependencies.json
# ├── reminders/
# │   ├── spec.md
# │   ├── analysis.md
# │   ├── tasks.md
# │   └── dependencies.json
# └── dependencies.json  (global)
```

### Scenario 2: Analyze Single Feature

```bash
# Analyze recurring tasks only
python agents/spec_agent.py --feature recurring-tasks

# Check results
cat specs/recurring-tasks/analysis.md
cat specs/recurring-tasks/dependencies.json
cat specs/recurring-tasks/tasks.md
```

### Scenario 3: Integration with SDD Workflow

```bash
# 1. Write spec
/sp.specify recurring-tasks "Add support for recurring tasks..."

# 2. Run spec agent
python agents/spec_agent.py --feature recurring-tasks

# 3. Review and create plan
/sp.plan recurring-tasks

# 4. Generate tasks
/sp.tasks recurring-tasks

# 5. Create ADRs (if prompted)
/sp.adr kafka-event-schema

# 6. Implement
/sp.implement recurring-tasks
```

---

## Integration Points

### With Existing Todo Phase 3

**Backend Integration**:
- Location: `../todo_phase3/backend/src/`
- Extend existing FastAPI routes
- Reuse authentication middleware
- Extend database models

**Frontend Integration**:
- Location: `../todo_phase3/frontend/`
- Extend existing Next.js app
- Reuse UI components from `components/`
- Integrate with existing API layer (`lib/api.ts`)

**Database Integration**:
- Extend existing PostgreSQL schema
- Create Alembic migrations
- Maintain backward compatibility

### With New Infrastructure

**Kafka**:
- Setup: Docker Compose or managed service
- Topics: Auto-created or pre-provisioned
- Schemas: JSON or Avro (recommend ADR)

**Dapr**:
- Runtime: Sidecar per service
- Components: YAML configuration files
- State store: Redis or PostgreSQL

---

## Validation & Testing

### Spec Agent Self-Test

```python
# tests/test_spec_agent.py

def test_spec_parser():
    """Test spec parsing functionality."""
    spec_content = """
---
name: recurring-tasks
priority: high
---

## Description
Support for recurring tasks with various patterns.

## Acceptance Criteria
- User can create daily recurring tasks
- User can create weekly recurring tasks

Kafka topic: task.scheduled
Dapr statestore required
Table: recurring_patterns
"""

    parser = SpecParser(Path("test_spec.md"))
    # Mock content
    parser.content = spec_content

    feature = parser.parse()

    assert feature.name == "recurring-tasks"
    assert feature.priority == "high"
    assert "task.scheduled" in feature.kafka_topics
    assert "statestore" in feature.dapr_components
    assert "recurring_patterns" in feature.db_tables


def test_dependency_analyzer():
    """Test dependency analysis."""
    features = [
        Feature(name="f1", kafka_topics=["topic.a"], ...),
        Feature(name="f2", kafka_topics=["topic.a", "topic.b"], ...)
    ]

    analyzer = DependencyAnalyzer(features)
    dep_map = analyzer.build_dependency_map()

    assert "topic.a" in dep_map.shared_infrastructure['kafka']
    assert "topic.b" in dep_map.shared_infrastructure['kafka']


def test_task_generator():
    """Test task generation."""
    feature = Feature(
        name="test-feature",
        kafka_topics=["test.topic"],
        dapr_components=["statestore"],
        db_tables=["test_table"],
        api_endpoints=["/api/test"],
        frontend_components=["TestComponent"],
        ...
    )

    generator = TaskGenerator(feature, DependencyMap(...))
    tasks_md = generator.generate_tasks_md()

    assert "Setup Kafka Topics" in tasks_md
    assert "Configure Dapr Components" in tasks_md
    assert "Create Database Migrations" in tasks_md
```

---

## Constraints & Invariants

**Constraints**:
- Spec files must follow SDD-RI format
- All features must have unique names
- Dependency map must be JSON-serializable
- Task IDs must be sequential integers

**Invariants**:
- Output artifacts are always regenerated (no manual edits)
- Dependency order is deterministic
- ADR suggestions never auto-execute
- All file paths are absolute or relative to project root

**Non-Goals**:
- Does NOT implement features (only analyzes)
- Does NOT modify existing code
- Does NOT execute database migrations
- Does NOT deploy infrastructure

---

## Follow-Up Work

1. **Enhance Spec Parser**:
   - Support for additional metadata (tags, owners, deadlines)
   - Better keyword extraction (NLP-based)
   - Multi-language spec support

2. **Dependency Visualization**:
   - Generate dependency graphs (Graphviz/Mermaid)
   - Interactive HTML reports
   - Dependency conflict detection

3. **Task Prioritization**:
   - Critical path analysis
   - Resource allocation suggestions
   - Time estimation (optional)

---

## Risk Factors

1. **Spec Quality**: Agent output quality depends on spec completeness
2. **Keyword Detection**: May miss dependencies if not mentioned explicitly
3. **Complexity Assessment**: Heuristic-based, may need calibration

---

## Architecture Decision Prompts

After running the Spec Agent, consider these ADRs:

1. **Kafka Topic Schema Design**:
   - JSON vs Avro vs Protobuf
   - Schema registry strategy
   - Versioning approach

2. **Dapr State Management**:
   - Redis vs PostgreSQL backing
   - State TTL policies
   - Consistency guarantees

3. **Database Migration Strategy**:
   - Zero-downtime migrations
   - Rollback procedures
   - Data backfill approach

---

**Last Updated**: 2026-02-02
**Maintained By**: Development Team
**Status**: Active Development
