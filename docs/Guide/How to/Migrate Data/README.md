# 🚛 Migrate data

This guide explains how to manage schema changes and migrations when using Django Structured JSON Field in your models.

## 📋 Overview

Django Structured JSON Field validates data against a schema both reading and writing from the database. This means that any changes to the schema require careful handling of migrations to ensure data integrity and compatibility.


### 🙈 Data overload

Django Structured JSON Field validations are performed only on declared attributes. Whenever you try to validate a python dictionary that has more keys than declared attributes, every key that is not declared will be ignored. This means that overload data will be filtered out and not saved to the database neither exposed to the user.

```python
# Example of overload data
from structured.pydantic import BaseModel

class MyModelSchema(BaseModel):
    name: str
    age: int

data = {
    "name": "John",
    "age": 30,
    "extra_field": "This will be ignored"
}
instance = MyModelSchema(**data)

instance.model_dump()
# Will output => {'name': 'John', 'age': 30}
```

## 🌟 Current Migration procedure

When you need to change the schema of a `StructuredJSONField`, you should follow these steps:

1. **Update the Schema**: Modify the schema class to reflect the new structure you want to enforce.
2. **Create a Migration**: Run `python manage.py generate_schema_migration <app_label> <model_name>` to create a new migration file that captures the changes to the schema.
3. **Review the Migration**: Check the generated migration file to ensure it correctly reflects the changes you made to the schema.
4. **Customize the Migration**: If necessary, customize the transformation functions as needed to handle any data transformations that has not been automatically generated.
5. **Run the Migration**: Execute `python manage.py migrate` to apply the migration to your database.
