#!/usr/bin/env python3
"""
Tasks Agent - Task Refiner for Todo App Phase 5
Transforms high-level plans into granular, actionable tasks.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class Task:
    """Represents a refined task."""
    id: str
    title: str
    description: str
    duration_hours: float
    steps: List[str]
    acceptance_criteria: List[str]
    test_cases: List[str]
    code_references: List[str]
    dependencies: List[str]
    phase: str
    complexity: str  # Simple, Medium, Complex
    file_paths: List[str]
    code_template: str = ""


class PlanParser:
    """Parses plan.md from Planning Agent."""

    def __init__(self, plan_path: Path):
        self.plan_path = plan_path
        self.content = plan_path.read_text(encoding='utf-8')

    def extract_phases(self) -> List[Dict]:
        """Extract all phases from plan."""
        phases = []
        pattern = r'### Phase \d+: (.+?)\n\*\*Duration\*\*: (.+?) \| \*\*Effort\*\*: (.+?)\n'
        matches = re.finditer(pattern, self.content, re.DOTALL)

        for match in matches:
            phases.append({
                'name': match.group(1).strip(),
                'duration': match.group(2).strip(),
                'effort': match.group(3).strip()
            })

        return phases

    def extract_tasks_from_phase(self, phase_name: str) -> List[Dict]:
        """Extract tasks from a specific phase."""
        # Find phase section
        pattern = rf'### Phase \d+: {re.escape(phase_name)}.*?(?=###|\Z)'
        match = re.search(pattern, self.content, re.DOTALL)

        if not match:
            return []

        phase_content = match.group(0)

        # Extract task checkboxes
        task_pattern = r'- \[ \] ([\d.]+) (.+?)(?:\n|$)'
        tasks = []

        for task_match in re.finditer(task_pattern, phase_content):
            tasks.append({
                'id': task_match.group(1).strip(),
                'title': task_match.group(2).strip(),
                'phase': phase_name
            })

        return tasks


class CodebaseAnalyzer:
    """Analyzes existing codebase for patterns."""

    def __init__(self, codebase_path: Path):
        self.codebase_path = codebase_path

    def find_similar_files(self, file_type: str) -> List[Path]:
        """Find similar files in codebase."""
        patterns = {
            'model': '**/models/*.py',
            'service': '**/services/*.py',
            'api': '**/api/*.py',
            'component': '**/components/*.tsx',
            'test': '**/tests/**/*.py'
        }

        pattern = patterns.get(file_type, '**/*')
        return list(self.codebase_path.glob(pattern))

    def extract_pattern(self, file_path: Path) -> str:
        """Extract code pattern from file."""
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception:
            return ""

    def get_code_reference(self, task_type: str) -> List[str]:
        """Get code references for task type."""
        references = {
            'model': [
                '../todo_phase3/backend/src/models/task.py',
                '../todo_phase3/backend/src/models/user.py'
            ],
            'service': [
                '../todo_phase3/backend/src/services/task_service.py'
            ],
            'api': [
                '../todo_phase3/backend/src/api/tasks.py',
                '../todo_phase3/backend/src/api/auth.py'
            ],
            'component': [
                '../todo_phase3/frontend/components/TaskForm.tsx',
                '../todo_phase3/frontend/components/TaskList.tsx'
            ]
        }

        return references.get(task_type, [])


class TaskRefiner:
    """Refines high-level tasks into granular implementation tasks."""

    def __init__(self, plan_parser: PlanParser, codebase_analyzer: CodebaseAnalyzer):
        self.plan_parser = plan_parser
        self.codebase_analyzer = codebase_analyzer

    def refine_database_task(self, task: Dict) -> List[Task]:
        """Refine database-related task."""
        refined = []

        # Schema design task
        refined.append(Task(
            id=f"{task['id']}.1",
            title=f"Design Database Schema - {task['title']}",
            description="Design database schema following existing conventions",
            duration_hours=2.0,
            steps=[
                "Review existing models",
                "Create schema design",
                "Define indexes and constraints",
                "Document relationships"
            ],
            acceptance_criteria=[
                "Schema includes all required fields",
                "Indexes defined for optimization",
                "Foreign keys properly defined"
            ],
            test_cases=[
                "Schema validation passes",
                "Constraints work correctly"
            ],
            code_references=self.codebase_analyzer.get_code_reference('model'),
            dependencies=[],
            phase=task['phase'],
            complexity="Medium",
            file_paths=["backend/src/models/"]
        ))

        # Migration task
        refined.append(Task(
            id=f"{task['id']}.2",
            title=f"Create Migration Script - {task['title']}",
            description="Create Alembic migration for schema",
            duration_hours=1.0,
            steps=[
                "Generate migration file",
                "Add upgrade() logic",
                "Add downgrade() logic",
                "Test migration locally"
            ],
            acceptance_criteria=[
                "Migration runs successfully",
                "Rollback works correctly",
                "No data loss"
            ],
            test_cases=[
                "Run migration up/down 3 times",
                "Verify schema matches design"
            ],
            code_references=[
                "../todo_phase3/backend/alembic/versions/"
            ],
            dependencies=[f"{task['id']}.1"],
            phase=task['phase'],
            complexity="Simple",
            file_paths=["backend/alembic/versions/"]
        ))

        return refined

    def refine_backend_task(self, task: Dict) -> List[Task]:
        """Refine backend API task."""
        refined = []

        # Model task
        refined.append(Task(
            id=f"{task['id']}.1",
            title=f"Create Data Model - {task['title']}",
            description="Create SQLAlchemy model",
            duration_hours=2.0,
            steps=[
                "Create model file",
                "Define model class",
                "Add relationships",
                "Implement validation"
            ],
            acceptance_criteria=[
                "Model matches schema",
                "Relationships correct",
                "Validation works"
            ],
            test_cases=[
                "Test model creation",
                "Test relationships",
                "Test validation"
            ],
            code_references=self.codebase_analyzer.get_code_reference('model'),
            dependencies=[],
            phase=task['phase'],
            complexity="Medium",
            file_paths=["backend/src/models/"],
            code_template="""
from sqlalchemy import Column, Integer, String
from .base import Base

class NewModel(Base):
    __tablename__ = "table_name"

    id = Column(Integer, primary_key=True)
    # Add fields here
"""
        ))

        # Service task
        refined.append(Task(
            id=f"{task['id']}.2",
            title=f"Create Service Layer - {task['title']}",
            description="Implement business logic",
            duration_hours=3.0,
            steps=[
                "Create service file",
                "Implement CRUD operations",
                "Add business logic",
                "Add error handling"
            ],
            acceptance_criteria=[
                "All operations work",
                "Proper error handling",
                "Unit tests >90% coverage"
            ],
            test_cases=[
                "Test CRUD operations",
                "Test business logic",
                "Test error scenarios"
            ],
            code_references=self.codebase_analyzer.get_code_reference('service'),
            dependencies=[f"{task['id']}.1"],
            phase=task['phase'],
            complexity="Complex",
            file_paths=["backend/src/services/"]
        ))

        # API endpoints task
        refined.append(Task(
            id=f"{task['id']}.3",
            title=f"Implement API Endpoints - {task['title']}",
            description="Create FastAPI route handlers",
            duration_hours=3.0,
            steps=[
                "Create API router file",
                "Define route handlers",
                "Add authentication",
                "Add validation",
                "Write API tests"
            ],
            acceptance_criteria=[
                "All endpoints functional",
                "Authentication enforced",
                "Validation works",
                "API tests passing"
            ],
            test_cases=[
                "Test each endpoint",
                "Test authentication",
                "Test validation",
                "Test error handling"
            ],
            code_references=self.codebase_analyzer.get_code_reference('api'),
            dependencies=[f"{task['id']}.2"],
            phase=task['phase'],
            complexity="Complex",
            file_paths=["backend/src/api/"]
        ))

        return refined

    def refine_frontend_task(self, task: Dict) -> List[Task]:
        """Refine frontend component task."""
        refined = []

        # Component task
        refined.append(Task(
            id=f"{task['id']}.1",
            title=f"Create Component - {task['title']}",
            description="Create React component",
            duration_hours=4.0,
            steps=[
                "Create component file",
                "Design component structure",
                "Implement state management",
                "Add API integration",
                "Add validation",
                "Write component tests"
            ],
            acceptance_criteria=[
                "Component renders correctly",
                "State management works",
                "API integration successful",
                "Tests passing"
            ],
            test_cases=[
                "Render test",
                "User interaction tests",
                "API integration tests",
                "Error handling tests"
            ],
            code_references=self.codebase_analyzer.get_code_reference('component'),
            dependencies=[],
            phase=task['phase'],
            complexity="Complex",
            file_paths=["frontend/components/"],
            code_template="""
import { useState } from 'react';

export default function NewComponent() {
  const [state, setState] = useState();

  return (
    <div>
      {/* Component JSX */}
    </div>
  );
}
"""
        ))

        return refined

    def refine_task(self, task: Dict) -> List[Task]:
        """Refine a task based on its type."""
        title_lower = task['title'].lower()

        if 'database' in title_lower or 'migration' in title_lower:
            return self.refine_database_task(task)
        elif 'backend' in title_lower or 'api' in title_lower:
            return self.refine_backend_task(task)
        elif 'frontend' in title_lower or 'component' in title_lower:
            return self.refine_frontend_task(task)
        else:
            # Generic refinement
            return [Task(
                id=task['id'],
                title=task['title'],
                description=task['title'],
                duration_hours=4.0,
                steps=["Implement task"],
                acceptance_criteria=["Task complete"],
                test_cases=["Verify functionality"],
                code_references=[],
                dependencies=[],
                phase=task['phase'],
                complexity="Medium",
                file_paths=[]
            )]


class OutputGenerator:
    """Generates output artifacts."""

    def generate_tasks_md(self, tasks: List[Task], feature_name: str) -> str:
        """Generate tasks-refined.md."""
        md = f"# Refined Tasks: {feature_name}\n\n"
        md += "**Generated by**: Tasks Agent\n"
        md += "**Status**: Ready for Implementation\n\n"
        md += "---\n\n"

        # Group by phase
        phases = {}
        for task in tasks:
            phases.setdefault(task.phase, []).append(task)

        for phase_name, phase_tasks in phases.items():
            md += f"## {phase_name}\n\n"

            for task in phase_tasks:
                md += f"### Task {task.id}: {task.title}\n\n"
                md += f"**Duration**: {task.duration_hours} hours\n"
                md += f"**Complexity**: {task.complexity}\n\n"
                md += f"**Description**: {task.description}\n\n"

                md += "**Steps**:\n"
                for step in task.steps:
                    md += f"1. {step}\n"
                md += "\n"

                md += "**Acceptance Criteria**:\n"
                for criterion in task.acceptance_criteria:
                    md += f"- [ ] {criterion}\n"
                md += "\n"

                md += "**Test Cases**:\n"
                for test in task.test_cases:
                    md += f"- {test}\n"
                md += "\n"

                if task.code_references:
                    md += "**Code References**:\n"
                    for ref in task.code_references:
                        md += f"- `{ref}`\n"
                    md += "\n"

                if task.dependencies:
                    md += f"**Dependencies**: {', '.join(task.dependencies)}\n\n"

                if task.code_template:
                    md += "**Code Template**:\n"
                    md += f"```python\n{task.code_template}\n```\n\n"

                md += "**File Paths**:\n"
                for path in task.file_paths:
                    md += f"- `{path}`\n"
                md += "\n"

                md += "---\n\n"

        return md

    def generate_github_issues(self, tasks: List[Task]) -> str:
        """Generate GitHub issues JSON."""
        issues = []

        for task in tasks:
            issue = {
                "title": f"Task {task.id}: {task.title}",
                "body": self._generate_issue_body(task),
                "labels": self._generate_labels(task),
                "milestone": f"{task.phase}",
                "assignees": []
            }
            issues.append(issue)

        return json.dumps(issues, indent=2)

    def _generate_issue_body(self, task: Task) -> str:
        """Generate issue body markdown."""
        body = f"## Description\n{task.description}\n\n"

        body += "## Steps\n"
        for i, step in enumerate(task.steps, 1):
            body += f"{i}. {step}\n"
        body += "\n"

        body += "## Acceptance Criteria\n"
        for criterion in task.acceptance_criteria:
            body += f"- [ ] {criterion}\n"
        body += "\n"

        body += "## Test Cases\n"
        for test in task.test_cases:
            body += f"- {test}\n"
        body += "\n"

        if task.code_references:
            body += "## Code References\n"
            for ref in task.code_references:
                body += f"- `{ref}`\n"
            body += "\n"

        body += f"## Estimates\n"
        body += f"- Duration: {task.duration_hours} hours\n"
        body += f"- Complexity: {task.complexity}\n\n"

        if task.dependencies:
            body += f"## Dependencies\n"
            for dep in task.dependencies:
                body += f"- Task {dep}\n"
            body += "\n"

        return body

    def _generate_labels(self, task: Task) -> List[str]:
        """Generate labels for task."""
        labels = [task.phase.lower().replace(" ", "-")]

        if 'database' in task.title.lower():
            labels.append("database")
        if 'api' in task.title.lower() or 'backend' in task.title.lower():
            labels.append("backend")
        if 'frontend' in task.title.lower() or 'component' in task.title.lower():
            labels.append("frontend")

        labels.append(f"complexity-{task.complexity.lower()}")

        return labels


class TasksAgent:
    """Main Tasks Agent orchestrator."""

    def __init__(self, feature_path: Path, codebase_path: Path):
        self.feature_path = feature_path
        self.codebase_path = codebase_path

        # Check if plan.md exists
        plan_file = feature_path / "plan.md"
        if not plan_file.exists():
            print(f"⚠️  Warning: plan.md not found in {feature_path}")
            print("   Using fallback: parsing from tasks.md instead")
            plan_file = feature_path / "tasks.md"

        self.plan_parser = PlanParser(plan_file)
        self.codebase_analyzer = CodebaseAnalyzer(codebase_path)
        self.task_refiner = TaskRefiner(self.plan_parser, self.codebase_analyzer)
        self.output_generator = OutputGenerator()

    def refine_all_tasks(self):
        """Refine all tasks from plan."""
        # For now, use simple task extraction from tasks.md
        # since we may not have plan.md yet
        tasks = self._extract_tasks_from_tasks_md()

        all_refined_tasks = []

        print(f"Found {len(tasks)} tasks to refine")

        for task in tasks:
            print(f"  Refining: {task['title']}")
            refined = self.task_refiner.refine_task(task)
            all_refined_tasks.extend(refined)

        # Generate outputs
        self._save_refined_tasks(all_refined_tasks)
        self._save_github_issues(all_refined_tasks)

        print(f"\n✅ Refined {len(all_refined_tasks)} tasks")
        print(f"\nOutputs saved to: {self.feature_path}")

    def _extract_tasks_from_tasks_md(self) -> List[Dict]:
        """Extract tasks from tasks.md as fallback."""
        tasks_file = self.feature_path / "tasks.md"
        if not tasks_file.exists():
            return []

        content = tasks_file.read_text(encoding='utf-8')
        tasks = []

        # Extract tasks
        pattern = r'## Task (\d+): (.+?)\n.*?\*\*Description\*\*: (.+?)\n'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            task_id = match.group(1)
            title = match.group(2).strip()
            description = match.group(3).strip()

            tasks.append({
                'id': task_id,
                'title': title,
                'description': description,
                'phase': 'Implementation'
            })

        return tasks

    def _save_refined_tasks(self, tasks: List[Task]):
        """Save refined tasks to markdown."""
        feature_name = self.feature_path.name
        tasks_md = self.output_generator.generate_tasks_md(tasks, feature_name)

        output_file = self.feature_path / "tasks-refined.md"
        output_file.write_text(tasks_md, encoding='utf-8')
        print(f"Tasks saved to: {output_file}")

    def _save_github_issues(self, tasks: List[Task]):
        """Save GitHub issues JSON."""
        issues_json = self.output_generator.generate_github_issues(tasks)

        output_file = self.feature_path / "github-issues.json"
        output_file.write_text(issues_json, encoding='utf-8')
        print(f"GitHub issues saved to: {output_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Tasks Agent - Refine implementation tasks")
    parser.add_argument('--feature', type=str, required=True,
                       help='Feature name (e.g., recurring-tasks)')
    parser.add_argument('--specs-dir', type=Path, default=Path('specs'),
                       help='Specs directory')
    parser.add_argument('--codebase', type=Path, default=Path('../todo_phase3'),
                       help='Existing codebase path')

    args = parser.parse_args()

    feature_path = args.specs_dir / args.feature

    if not feature_path.exists():
        print(f"Error: Feature path not found: {feature_path}")
        return

    agent = TasksAgent(feature_path, args.codebase)
    agent.refine_all_tasks()

    print("\n✅ Task refinement complete!")
    print("\nNext steps:")
    print("1. Review tasks-refined.md")
    print("2. Create GitHub issues (optional)")
    print("3. Begin implementation: /sp.implement")


if __name__ == '__main__':
    main()
