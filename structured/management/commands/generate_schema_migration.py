from django.core.management.base import BaseCommand
from django.apps import apps
import os
from structured.fields import StructuredJSONField
from structured.migrations.structured_json_migration import (
    StructuredJSONMigrationGenerator,
)


class Command(BaseCommand):
    help = "Generate migration for StructuredJSONField schema changes"

    def add_arguments(self, parser):
        parser.add_argument("app_label", type=str, help="App label")
        parser.add_argument("model_name", type=str, help="Model name")
        parser.add_argument(
            "--field_name", type=str, help="Field name", default=None, required=False
        )
        parser.add_argument(
            "--analyze-only",
            action="store_true",
            help="Only analyze errors without generating migration",
        )

    def handle(self, *args, **options):
        self.options = options
        try:
            # Get the model
            model_class = apps.get_model(options["app_label"], options["model_name"])

            field_name = options.get("field_name")
            migrations = []
            for field in model_class._meta.get_fields():
                if isinstance(field, StructuredJSONField) and (
                    field_name is None or field.name == field_name
                ):
                    migration = self.handle_single_field(
                        model_class, field.name, analyze_only=options["analyze_only"]
                    )
                    if isinstance(migration, str):
                        migrations.append(migration)

            if len(migrations) == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'No migrations needed for model {options["app_label"]}.{options["model_name"]}.'
                    )
                )
                return
            self.stdout.write(
                self.style.WARNING(
                    "IMPORTANT: Please review and customize the transformation functions before running the migration."
                )
            )
            self.stdout.write("Next steps:")
            self.stdout.write(
                f"1. Review the generated migration files: [{', '.join(migrations)}]"
            )
            self.stdout.write("2. Customize the transformation functions as needed")
            self.stdout.write(
                f"3. Run: python manage.py migrate {options['app_label']}"
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error loading model {options['app_label']}.{options['model_name']}: {str(e)}"
                )
            )
            return

    def handle_single_field(self, model_class, field_name, analyze_only=False):
        """
        Handle migration for a single field in a model.
        """
        try:
            # Get the field
            field = model_class._meta.get_field(field_name)

            # Use current field schema
            if not hasattr(field, "schema"):
                self.stdout.write(
                    self.style.ERROR(
                        f"Field {field_name} doesn't have a schema_class attribute"
                    )
                )
                return
            schema_class = field.schema
            schema_class_name = ""
            if hasattr(schema_class, "__name__"):
                schema_class_name = schema_class.__name__
            else:
                schema_class_name = str(schema_class)

            self.stdout.write(f"Using field schema: {schema_class_name}")

            # Generate migration
            generator = StructuredJSONMigrationGenerator(
                model_class, field_name, schema_class
            )

            self.stdout.write("Analyzing existing data...")
            validation_errors = generator.analyze_validation_errors()

            if not validation_errors:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'No validation errors found. No migration needed for field "{field_name}".'
                    )
                )
                return

            # Show error summary
            self.stdout.write(
                f"\nFound validation errors in {len(validation_errors)} records:"
            )

            error_summary = {}
            for record_id, record_errors in validation_errors.items():
                for error in record_errors:
                    error_key = (
                        f"{'.'.join(str(loc) for loc in error['loc'])}:{error['type']}"
                    )
                    if error_key not in error_summary:
                        error_summary[error_key] = []
                    error_summary[error_key].append(record_id)

            for error_pattern, affected_records in error_summary.items():
                field_path, error_type = error_pattern.split(":", 1)
                self.stdout.write(
                    f"  - {field_path} ({error_type}): {len(affected_records)} records"
                )

            if analyze_only:
                self.stdout.write("\nUse --analyze-only=false to generate migration.")
                return

            # Generate migration content
            self.stdout.write("\nGenerating migration...")
            migration_content, migration_number = generator.generate_migration_template(
                validation_errors
            )

            migration_name = f"{migration_number}_migrate_{field_name}_schema.py"

            app_config = apps.get_app_config(self.options["app_label"])
            migrations_dir = os.path.join(app_config.path, "migrations")

            # Ensure migrations directory exists
            os.makedirs(migrations_dir, exist_ok=True)

            migration_path = os.path.join(migrations_dir, migration_name)

            with open(migration_path, "w") as f:
                f.write(migration_content)

            self.stdout.write(
                self.style.SUCCESS(f"\nMigration generated: {migration_path}")
            )
            return migration_path
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error generating migration: {str(e)}"))
            if self.options.get("verbosity", 1) > 1:
                import traceback

                self.stdout.write(traceback.format_exc())
