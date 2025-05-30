from pydantic import ValidationError
from typing import Dict, List, Any, Callable, Tuple
from dataclasses import dataclass
import os
from django.apps import apps


@dataclass
class FieldMigrationRule:
    """Represents a migration rule for a specific field validation error."""
    field_path: str
    error_type: str
    transformation: Callable[[Any], Any]
    description: str


class StructuredJSONMigrationGenerator:
    """Generates Django migrations for StructuredJSONField schema changes."""

    def __init__(self, model_class, field_name: str, new_schema_class=None):
        self.model_class = model_class
        self.field_name = field_name
        self.schema_class = new_schema_class
        if not self.schema_class:
            field = model_class._meta.get_field(field_name)
            self.schema_class = getattr(field, 'schema', None)
        if not self.schema_class:
            raise ValueError(f"Field {field_name} does not have a schema class defined.")
        self.migration_rules: List[FieldMigrationRule] = []

    def analyze_validation_errors(self) -> Dict[str, List[Dict]]:
        """Analyze existing data and collect validation errors."""
        validation_errors = {}

        raw_data_attr = f"{self.field_name}_raw"
        for instance in self.model_class.objects.all().only('pk', self.field_name):
            try:
                field_data = getattr(instance, raw_data_attr)
                if field_data:
                    # Try to validate with new schema
                    self.schema_class.validate_python(field_data)
            except ValidationError as e:
                validation_errors[f"{instance.pk}"] = [
                    {
                        'loc': error['loc'],
                        'msg': error['msg'],
                        'type': error['type'],
                        'input': error.get('input'),
                        'ctx': error.get('ctx', {})
                    }
                    for error in e.errors()
                ]
        return validation_errors

    def generate_migration_template(self, validation_errors: Dict) -> Tuple[str, str]:
        """Generate a Django migration template with transformation functions."""

        # Analyze common error patterns
        error_patterns = self._analyze_error_patterns(validation_errors)

        # Get the latest migration for dependencies
        dependencies = self._get_migration_dependencies()

        migration_number = self._get_migration_number()

        migration_template = f'''# Generated migration for {self.model_class.__name__}.{self.field_name}
# Schema change detected - please review and customize the transformations below

from django.db import migrations
import json


def transform_{self.field_name}_data(apps, schema_editor):
    """
    Transform existing {self.field_name} data to match new schema.

    Validation errors found:
{self._format_error_summary(error_patterns)}
    """
    {self.model_class.__name__} = apps.get_model('{self.model_class._meta.app_label}', '{self.model_class.__name__}')

    # Process each record
    for instance in {self.model_class.__name__}.objects.all():
        if not getattr(instance, '{self.field_name}_raw'):
            continue

        data = getattr(instance, '{self.field_name}_raw')
        transformed_data = transform_record(data, instance.pk)
        setattr(instance, '{self.field_name}', transformed_data)
        instance.save(update_fields=['{self.field_name}'])


def transform_record(data: dict, record_id: int) -> dict:
    """
    Transform a single record's data.

    Args:
        data: The current JSON data
        record_id: The record's primary key for reference

    Returns:
        Transformed data dictionary
    """
    transformed = data.copy()

    # TODO: Implement your transformations below
    # Each transformation addresses specific validation errors

{self._generate_transformation_functions(error_patterns)}

    return transformed


def reverse_transform_{self.field_name}_data(apps, schema_editor):
    """
    Reverse transformation - implement if the migration should be reversible.
    """
    # TODO: Implement reverse transformation if needed
    pass


class Migration(migrations.Migration):

    dependencies = [
        {self._format_dependencies(dependencies)}
    ]

    operations = [
        migrations.RunPython(
            transform_{self.field_name}_data,
            reverse_transform_{self.field_name}_data,
        ),
    ]
'''
        return migration_template, migration_number

    def _analyze_error_patterns(self, validation_errors: Dict) -> Dict[str, List]:
        """Analyze validation errors to find common patterns."""
        patterns = {}

        for record_id, errors in validation_errors.items():
            for error in errors:
                error_key = f"{'.'.join(str(loc) for loc in error['loc'])}:{error['type']}"
                if error_key not in patterns:
                    patterns[error_key] = []
                patterns[error_key].append({
                    'record_id': record_id,
                    'error': error
                })

        return patterns

    def _format_error_summary(self, error_patterns: Dict) -> str:
        """Format error patterns for the migration template."""
        summary_lines = []
        for pattern, occurrences in error_patterns.items():
            field_path, error_type = pattern.split(':', 1)
            count = len(occurrences)
            example_error = occurrences[0]['error']

            summary_lines.append(f"    - Field '{field_path}' ({error_type}): {count} records")
            summary_lines.append(f"      Example: {example_error['msg']}")

        return '\n'.join(summary_lines)

    def _generate_transformation_functions(self, error_patterns: Dict) -> str:
        """Generate transformation function templates for each error pattern."""
        transformations = []

        for pattern, occurrences in error_patterns.items():
            field_path, error_type = pattern.split(':', 1)
            example_error = occurrences[0]['error']

            transformation = self._create_transformation_template(
                field_path, error_type, example_error
            )
            transformations.append(transformation)

        return '\n'.join(transformations)

    def _create_transformation_template(self, field_path: str, error_type: str, example_error: Dict) -> str:
        """Create a transformation template for a specific error type."""
        field_parts = field_path.split('.')

        if error_type == 'missing':
            return f'''    # Handle missing field: {field_path}
    # Error: {example_error['msg']}
    if {self._build_field_check(field_parts, 'not in')}:
        {self._build_field_assignment(field_parts, 'None  # TODO: Set appropriate default value')}
'''

        elif error_type == 'string_type':
            return f'''    # Handle type conversion: {field_path}
    # Error: {example_error['msg']}
    if {self._build_field_check(field_parts, 'in')} and not isinstance({self._build_field_access(field_parts)}, str):
        {self._build_field_assignment(field_parts, f'str({self._build_field_access(field_parts)})')}
'''

        elif error_type == 'int_type':
            return f'''    # Handle type conversion: {field_path}
    # Error: {example_error['msg']}
    if {self._build_field_check(field_parts, 'in')}:
        try:
            {self._build_field_assignment(field_parts, f'int({self._build_field_access(field_parts)})')}
        except (ValueError, TypeError):
            {self._build_field_assignment(field_parts, '0  # TODO: Set appropriate default value')}
'''

        elif error_type == 'extra_forbidden':
            return f'''    # Remove forbidden extra field: {field_path}
    # Error: {example_error['msg']}
    if {self._build_field_check(field_parts, 'in')}:
        {self._build_field_deletion(field_parts)}
'''

        else:
            return f'''    # Handle {error_type}: {field_path}
    # Error: {example_error['msg']}
    # TODO: Implement transformation for {error_type}
    if {self._build_field_check(field_parts, 'in')}:
        pass  # Add your transformation logic here
'''

    def _build_field_check(self, field_parts: List[str], operation: str) -> str:
        """Build a field existence check."""
        if len(field_parts) == 1:
            return f"'{field_parts[0]}' {operation} transformed"

        checks = []
        current_path = "transformed"
        for part in field_parts[:-1]:
            checks.append(f"'{part}' in {current_path}")
            current_path += f"['{part}']"

        final_check = f"'{field_parts[-1]}' {operation} {current_path}"

        if operation == 'in':
            return ' and '.join(checks + [final_check])
        else:  # 'not in'
            return final_check if len(checks) == 0 else f"({' and '.join(checks)}) and {final_check}"

    def _build_field_access(self, field_parts: List[str]) -> str:
        """Build field access code."""
        access = "transformed"
        for part in field_parts:
            access += f"['{part}']"
        return access

    def _build_field_assignment(self, field_parts: List[str], value: str) -> str:
        """Build field assignment code."""
        return f"{self._build_field_access(field_parts)} = {value}"

    def _build_field_deletion(self, field_parts: List[str]) -> str:
        """Build field deletion code."""
        if len(field_parts) == 1:
            return f"del transformed['{field_parts[0]}']"

        parent_access = "transformed"
        for part in field_parts[:-1]:
            parent_access += f"['{part}']"

        return f"del {parent_access}['{field_parts[-1]}']"

    def _get_migration_dependencies(self) -> List[tuple]:
        """Get the latest migration dependencies for this app."""

        app_config = apps.get_app_config(self.model_class._meta.app_label)
        migrations_dir = os.path.join(app_config.path, 'migrations')

        dependencies = []

        if os.path.exists(migrations_dir):
            # Find the latest migration file
            migration_files = [
                f for f in os.listdir(migrations_dir)
                if f.endswith('.py') and f != '__init__.py' and not f.startswith('.')
            ]

            if migration_files:
                # Sort to get the latest migration
                migration_files.sort()
                latest_migration = migration_files[-1].replace('.py', '')
                dependencies.append((self.model_class._meta.app_label, latest_migration))
            else:
                # No migrations yet, depend on initial
                dependencies.append((self.model_class._meta.app_label, '__first__'))

        return dependencies

    def _format_dependencies(self, dependencies: List[tuple]) -> str:
        """Format dependencies for the migration file."""
        if not dependencies:
            return "        # No dependencies"

        formatted_deps = []
        for app_label, migration_name in dependencies:
            formatted_deps.append(f"        ('{app_label}', '{migration_name}'),")

        return '\n'.join(formatted_deps)

    def _get_migration_number(self):
        app_config = apps.get_app_config(self.model_class._meta.app_label)
        migrations_dir = os.path.join(app_config.path, 'migrations')
        migration_files = [
            f for f in os.listdir(migrations_dir)
            if f.endswith('.py') and f != '__init__.py' and not f.startswith('.')
        ]
        migration_files.sort()
        if migration_files:
            latest_migration = migration_files[-1].replace('.py', '')
            migration_number = int(latest_migration.split('_')[0])
        else:
            migration_number = 0
        migration_number += 1
        return f"{migration_number:04d}"
