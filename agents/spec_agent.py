#!/usr/bin/env python3
"""
Spec Agent - Specification Analyzer for Todo App Phase 5
Parses specs, identifies dependencies, generates structured plans.

Version: 1.0.0
Author: Development Team
Date: 2026-02-02
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass, asdict, field
import yaml
import sys


@dataclass
class Feature:
    """Represents a parsed feature specification."""
    name: str
    description: str = ""
    category: str = "general"
    acceptance_criteria: List[str] = field(default_factory=list)
    complexity: int = 5  # 1-10
    priority: str = "medium"  # high, medium, low
    dependencies: List[str] = field(default_factory=list)
    kafka_topics: List[str] = field(default_factory=list)
    dapr_components: List[str] = field(default_factory=list)
    db_tables: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    frontend_components: List[str] = field(default_factory=list)


@dataclass
class DependencyMap:
    """Maps all dependencies across features."""
    features: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)
    shared_infrastructure: Dict[str, List[str]] = field(default_factory=dict)
    external_services: List[str] = field(default_factory=list)


class SpecParser:
    """Parses specification markdown files."""

    def __init__(self, spec_path: Path):
        self.spec_path = spec_path
        self.content = spec_path.read_text(encoding='utf-8')

    def extract_front_matter(self) -> Dict[str, Any]:
        """Extract YAML front matter from spec."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', self.content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError as e:
                print(f"Warning: Failed to parse YAML front matter: {e}")
                return {}
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

    def identify_shared_resources(self) -> Dict[str, Dict[str, List[str]]]:
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
                [],
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
        self.specs_dir = Path(specs_dir)
        self.output_dir = Path(output_dir) if output_dir else self.specs_dir
        self.features: List[Feature] = []

    def analyze_all_specs(self):
        """Analyze all spec files in specs directory."""
        spec_files = list(self.specs_dir.rglob("spec.md"))

        print(f"Found {len(spec_files)} spec files")

        if not spec_files:
            print(f"No spec.md files found in {self.specs_dir}")
            print("Please create specs using the format: specs/<feature-name>/spec.md")
            return

        for spec_file in spec_files:
            print(f"\nAnalyzing: {spec_file}")
            try:
                parser = SpecParser(spec_file)
                feature = parser.parse()
                self.features.append(feature)

                # Generate outputs
                self._generate_analysis(feature, spec_file.parent)
                self._generate_tasks(feature, spec_file.parent)
            except Exception as e:
                print(f"Error analyzing {spec_file}: {e}")
                continue

        if self.features:
            self.generate_dependency_map()

    def analyze_feature(self, feature_name: str):
        """Analyze a specific feature."""
        spec_file = self.specs_dir / feature_name / "spec.md"

        if not spec_file.exists():
            print(f"Error: Spec file not found: {spec_file}")
            print(f"\nPlease create the spec file first:")
            print(f"  mkdir -p {self.specs_dir / feature_name}")
            print(f"  # Create {spec_file}")
            return

        print(f"Analyzing: {spec_file}")
        try:
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
        except Exception as e:
            print(f"Error analyzing feature: {e}")
            raise

    def generate_dependency_map(self):
        """Generate comprehensive dependency map."""
        analyzer = DependencyAnalyzer(self.features)
        dep_map = analyzer.build_dependency_map()
        shared = analyzer.identify_shared_resources()

        # Save to root specs directory
        self._save_dependency_map(dep_map, self.specs_dir)

        # Save shared resources report
        shared_file = self.output_dir / "shared-resources.json"
        shared_file.write_text(json.dumps(shared, indent=2), encoding='utf-8')
        print(f"\nShared resources saved to: {shared_file}")

    def _generate_analysis(self, feature: Feature, output_dir: Path):
        """Generate feature analysis report."""
        analysis = f"""# Feature Analysis: {feature.name}

**Category**: {feature.category}
**Priority**: {feature.priority}
**Complexity**: {feature.complexity}/10

## Description

{feature.description or 'No description provided.'}

## Acceptance Criteria

{chr(10).join(f"- {criterion}" for criterion in feature.acceptance_criteria) or '- No criteria specified'}

## Dependencies

### Infrastructure
- **Kafka Topics**: {', '.join(feature.kafka_topics) or 'None'}
- **Dapr Components**: {', '.join(feature.dapr_components) or 'None'}
- **Database Tables**: {', '.join(feature.db_tables) or 'None'}

### API
- **Endpoints**:
{chr(10).join(f"  - {ep}" for ep in feature.api_endpoints) or '  - None'}

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
        analysis_file.write_text(analysis, encoding='utf-8')
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

        if not feature.acceptance_criteria:
            recommendations.append("- ⚠️  Add acceptance criteria to spec.md")

        return '\n'.join(recommendations) or "- No specific recommendations"

    def _generate_tasks(self, feature: Feature, output_dir: Path):
        """Generate tasks.md for feature."""
        # Build minimal dependency map for this feature
        analyzer = DependencyAnalyzer([feature])
        dep_map = analyzer.build_dependency_map()

        generator = TaskGenerator(feature, dep_map)
        tasks_md = generator.generate_tasks_md()

        tasks_file = output_dir / "tasks.md"
        tasks_file.write_text(tasks_md, encoding='utf-8')
        print(f"Tasks saved to: {tasks_file}")

    def _save_dependency_map(self, dep_map: DependencyMap, output_dir: Path):
        """Save dependency map as JSON."""
        dep_file = output_dir / "dependencies.json"
        dep_file.write_text(json.dumps(asdict(dep_map), indent=2), encoding='utf-8')
        print(f"Dependencies saved to: {dep_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Spec Agent - Analyze Todo App specifications")
    parser.add_argument('--input', type=Path, default=Path('specs'),
                       help='Input specs directory (default: specs)')
    parser.add_argument('--output', type=Path, default=None,
                       help='Output directory (defaults to input)')
    parser.add_argument('--feature', type=str, default=None,
                       help='Analyze specific feature only')

    args = parser.parse_args()

    print("=" * 60)
    print("Spec Agent - Specification Analyzer")
    print("Version 1.0.0")
    print("=" * 60)

    agent = SpecAgent(args.input, args.output)

    try:
        if args.feature:
            agent.analyze_feature(args.feature)
        else:
            agent.analyze_all_specs()

        print("\n" + "=" * 60)
        print("[SUCCESS] Spec analysis complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review generated analysis.md files")
        print("2. Check dependencies.json for infrastructure requirements")
        print("3. Review tasks.md files")
        print("4. Create ADRs for suggested architectural decisions")
        print(f"\nGenerated files location: {agent.output_dir.absolute()}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
