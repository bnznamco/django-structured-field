# 🔗 Relationships

This guide covers how to work with different types of relationships in Django Structured JSON Field.

## 🔄 Types of Relationships

The field supports three main types of relationships:
1. 📦 Recursive relationships
2. 🔑 Foreign Key relationships
3. 🔀 Many-to-Many relationships (QuerySet fields)

## 📦 Recursive Relationships

Recursive relationships allow you to create self-referential structures in your schema.

### 🧩 Basic Recursion

```python
from typing import Optional, List
from structured.pydantic.models import BaseModel

class MySchema(BaseModel):
    name: str
    age: int = None
    parent: Optional['MySchema'] = None
    relateds: List['MySchema'] = []
```

### 🚀 Usage Example

```python
# Create a parent instance
parent = MySchema(name="Parent", age=40)

# Create a child instance
child = MySchema(name="Child", age=10, parent=parent)

# Create a model instance
model_instance = MyModel.objects.create(
    title="Example",
    structured_data=child
)

# Access the parent
print(model_instance.structured_data.parent.name)  # "Parent"
```

## 🔑 Foreign Key Relationships

Foreign Key relationships allow you to reference other Django models in your schema.

### 🧩 Using ForeignKey Field

```python
from structured.pydantic.fields import ForeignKey
from structured.pydantic.models import BaseModel
from myapp.models import SomeModel

class MySchema(BaseModel):
    name: str
    age: int = None
    fk_field: ForeignKey[SomeModel] = None
```

### 🔄 Alternative Syntax

You can also use the model class directly as the type annotation:

```python
from structured.pydantic.models import BaseModel
from myapp.models import SomeModel

class MySchema(BaseModel):
    name: str
    age: int = None
    fk_field: SomeModel = None
```

The field will still be treated as a ForeignKey if the type annotation is a subclass of Django `models.Model`.

### 🚀 Usage Example

```python
from myapp.models import SomeModel

# Create a related model instance
related_model = SomeModel.objects.create(name="Related")

# Create a schema with foreign key
schema = MySchema(
    name="Main",
    age=30,
    fk_field=related_model
)

# Create a model instance
model_instance = MyModel.objects.create(
    title="Example",
    structured_data=schema
)

# Or create using a dictionary with the ID of the related model
model_instance = MyModel.objects.create(
    title="Example",
    structured_data={
        "name": "Main",
        "age": 30,
        "fk_field": related_model.id  # Using the ID directly
    }
)

# Access the foreign key
print(model_instance.structured_data.fk_field.name)  # "Related"
```

## 🧠 Abstract Models as Foreign Keys

You can also use abstract models as foreign keys:

```python
from django.db import models
from structured.pydantic.fields import ForeignKey
from structured.pydantic.models import BaseModel

class AbstractModel(models.Model):
    common_field = models.CharField(max_length=100)
    
    class Meta:
        abstract = True

class ConcreteModel1(AbstractModel):
    specific_field = models.CharField(max_length=100)

class ConcreteModel2(AbstractModel):
    another_field = models.CharField(max_length=100)

class MySchema(BaseModel):
    name: str
    age: int = None
    abstract_fk: ForeignKey[AbstractModel] = None
```

Usage:

```python
# The field will accept any model that inherits from AbstractModel
instance1 = ConcreteModel1.objects.create(common_field="test1", specific_field="test2")
instance2 = ConcreteModel2.objects.create(common_field="test3", another_field="test4")

# Both can be used in the abstract_fk field
model_instance = MyModel.objects.create(
    title="Example",
    structured_data=MySchema(name="Test", age=25, abstract_fk=instance1)
)

# You can change the related model to a different subclass
model_instance.structured_data.abstract_fk = instance2
model_instance.save()
```

## 🔀 Many-to-Many Relationships (QuerySet Fields)

Many-to-Many relationships are handled using the `QuerySet` field.

### 🧩 Using QuerySet Field

```python
from structured.pydantic.fields import QuerySet
from structured.pydantic.models import BaseModel
from myapp.models import SomeModel

class MySchema(BaseModel):
    name: str
    age: int = None
    qs_field: QuerySet[SomeModel]
```

### 🚀 Usage Example

```python
from myapp.models import SomeModel

# Create some related instances
related_instances = SomeModel.objects.bulk_create([
    SomeModel(name="Related1"),
    SomeModel(name="Related2"),
    SomeModel(name="Related3")
])

# Create a schema with a queryset
schema = MySchema(
    name="Main",
    age=30,
    qs_field=SomeModel.objects.all()  # Using a QuerySet
)

# Create a model instance
model_instance = MyModel.objects.create(
    title="Example",
    structured_data=schema
)

# Or create using a dictionary with the IDs of the related models
model_instance = MyModel.objects.create(
    title="Example",
    structured_data={
        "name": "Main",
        "age": 30,
        "qs_field": [1, 2, 3]  # Using a list of IDs
    }
)

# Query the related objects
filtered = model_instance.structured_data.qs_field.filter(name__startswith='Related')
count = model_instance.structured_data.qs_field.count()
first = model_instance.structured_data.qs_field.first()

# Change the queryset
model_instance.structured_data.qs_field = SomeModel.objects.filter(name="Related1")
model_instance.save()
```

### 🔄 QuerySet Order Preservation

The QuerySet field maintains the order of the given QuerySet:

```python
# Create with ordered queryset
model_instance = MyModel.objects.create(
    title="Example",
    structured_data={
        "name": "Main",
        "age": 30,
        "qs_field": SomeModel.objects.all().order_by("name")
    }
)

# Access ordered queryset
first = model_instance.structured_data.qs_field.first()  # First alphabetically
last = model_instance.structured_data.qs_field.last()    # Last alphabetically
```

## 📦 Nested Relationships

You can combine these relationship types in nested structures:

```python
class ChildSchema(BaseModel):
    name: str
    age: int = None
    fk_field: SomeModel = None
    qs_field: QuerySet[SomeModel]

class ParentSchema(BaseModel):
    name: str
    age: int = None
    fk_field: SomeModel = None
    child: ChildSchema = None
```

Usage:

```python
child_data = ChildSchema(
    name="Child",
    age=10,
    fk_field=related_model2,
    qs_field=SomeModel.objects.filter(name__in=["Related3", "Related4"])
)

parent_data = ParentSchema(
    name="Parent",
    age=40,
    fk_field=related_model1,
    child=child_data
)

model_instance = MyModel.objects.create(
    title="Example",
    structured_data=parent_data
)

# Access nested relationships
parent_fk = model_instance.structured_data.fk_field.name
child_fk = model_instance.structured_data.child.fk_field.name
child_qs_count = model_instance.structured_data.child.qs_field.count()
```

## Best Practices

1. **Recursive Relationships**:
   - Use `Optional` for single references
   - Use `List` for multiple references
   - Be careful with circular references to avoid infinite loops

2. **Foreign Key Relationships**:
   - Always provide a default value (usually `None`)
   - Consider using the direct model class syntax for simplicity
   - Handle potential null values in your code

3. **Many-to-Many Relationships**:
   - Use `QuerySet` for flexible querying
   - Consider performance implications of large querysets
   - Use appropriate filtering to limit queryset size

## Common Issues and Solutions

1. **Circular Imports**:
   - Use string literals for model references (`'ModelName'`)
   - Import models at the function level if needed

2. **Performance**:
   - Enable caching to optimize query performance
   - Use appropriate indexing on related fields
   - Use `select_related()` for foreign keys when fetching models

3. **Validation**:
   - Ensure related objects exist before assignment
   - Handle null values appropriately
   - Validate queryset results before assignment

## Next Steps

After understanding relationships, you might want to explore:
- [Admin Integration](../Admin%20Integration/README.md) for managing relationships in the Django admin
- [REST Framework Integration](../REST%20Framework%20Integration/README.md) for API endpoints
- [Caching](../Caching/README.md) for optimizing relationship queries 