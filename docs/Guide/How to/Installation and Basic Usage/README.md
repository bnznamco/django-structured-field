# 📦 Installation and Basic Usage

This guide will help you get started with Django Structured JSON Field.

## 🚀 Installation

Install the package using pip:

```bash
pip install django-structured-json-field
```

## 🧩 Basic Usage

### 1️⃣ Define Your Schema

First, you need to define your schema using Pydantic models. Create a new file (e.g., `schemas.py`) and define your schema:

```python
from structured.pydantic.models import BaseModel

# Define your schema using Pydantic models
class MySchema(BaseModel):
    name: str
    age: int = None

# Define an initialization function
def init_data():
    return MySchema(name='')
```

### 2️⃣ Create Your Model

Now, create a Django model that uses the StructuredJSONField:

```python
from django.db import models
from structured.fields import StructuredJSONField

class MyModel(models.Model):
    title = models.CharField(max_length=100)
    structured_data = StructuredJSONField(schema=MySchema, default=init_data)
```

### 3️⃣ Create and Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4️⃣ Using the Model

You can now use your model as you would with any other Django model:

```python
# Create a new instance with a dictionary
instance = MyModel.objects.create(
    title="Example",
    structured_data={"name": "John Doe", "age": 30}
)

# Or create with a schema instance
schema_instance = MySchema(name="John Doe", age=30)
instance = MyModel.objects.create(
    title="Example",
    structured_data=schema_instance
)

# Access the structured data
print(instance.structured_data.name)  # "John Doe"
print(instance.structured_data.age)   # 30

# Update the structured data
instance.structured_data.age = 31
instance.save()
```

## 🔑 Key Concepts

1. **📐 Schema Definition**: Your schema defines the structure and validation rules for your JSON field.
2. **🔄 Default Values**: The `init_data` function provides default values for new instances.
3. **✅ Type Validation**: The field automatically validates data against your schema.
4. **🚫 Null Values**: Fields can be optional by providing default values (like `None`).
5. **📥 Data Input**: You can provide either a dictionary or a schema instance when creating or updating records.

## 💡 Best Practices

1. Always define an initialization function (`init_data`) to provide default values.
2. Use type hints in your schema for better IDE support and validation.
3. Consider making fields optional if they're not always required.
4. Use descriptive field names that clearly indicate their purpose.
5. Test your schema with both dictionary and object inputs to ensure it works correctly.

## ❓ Common Issues and Solutions

1. **🚧 Migration Errors**: If you encounter migration errors, ensure your schema is properly defined before running migrations.
2. **⚠️ Validation Errors**: The field will raise validation errors if the data doesn't match your schema.
3. **🔄 Default Values**: Always provide appropriate default values to prevent null value issues.

## 📦 Nested Structures

You can also define nested schemas:

```python
class ChildSchema(BaseModel):
    name: str
    age: int = None

class ParentSchema(BaseModel):
    name: str
    age: int = None
    child: ChildSchema = None
```

Example usage:

```python
# Create with nested data
instance = MyModel.objects.create(
    title="Example",
    structured_data={
        "name": "Parent",
        "age": 40,
        "child": {
            "name": "Child",
            "age": 10
        }
    }
)

# Access nested fields
print(instance.structured_data.child.name)  # "Child"
```

## 🔄 Next Steps

After mastering basic usage, you might want to explore:
- [🔗 Relationships](../Relationships/README.md)
- [🧰 Admin Integration](../Admin%20Integration/README.md)
- [🌍 REST Framework Integration](../REST%20Framework%20Integration/README.md) 