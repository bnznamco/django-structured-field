# 🌍 REST Framework Integration
This guide explains how to integrate Django Structured JSON Field with Django Rest Framework (DRF).

## 🚀 Basic Setup

### 1️⃣ Install Dependencies
Make sure you have Django Rest Framework installed:
```bash
pip install djangorestframework
```

### 2️⃣ Configure Settings
Add 'rest_framework' to your INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'structured',
    
    # Your apps
    'myapp',
]
```

## 🧩 Using StructuredModelSerializer

The package provides a special serializer class called `StructuredModelSerializer` that automatically handles the serialization and deserialization of structured fields.

### 📌 Basic Usage

Simply use `StructuredModelSerializer` instead of the standard DRF `ModelSerializer`:

```python
from rest_framework import serializers
from structured.contrib.rest_framework import StructuredModelSerializer
from .models import MyModel

class MyModelSerializer(StructuredModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'
```

That's it! The serializer will automatically handle your structured fields, including:
- Proper serialization of nested data
- Validation based on your Pydantic schema
- Translation of Pydantic validation errors to DRF errors
- Handling of related models (ForeignKey and QuerySet fields)

### ⚙️ How It Works

When you use `StructuredModelSerializer`:

1. For **serialization** (Python → JSON):
   - Structured fields are automatically converted to their JSON representation
   - Foreign keys are serialized as their IDs
   - QuerySets are serialized as lists of IDs

2. For **deserialization** (JSON → Python):
   - JSON data is validated against your Pydantic schema
   - Foreign keys are converted to model instances
   - Lists of IDs are converted to QuerySets

### 📊 Example Response

A model with a structured field:

```python
class PersonSchema(BaseModel):
    name: str
    age: int = None
    friends: QuerySet[User]  # A Django User model

class Person(models.Model):
    title = models.CharField(max_length=100)
    data = StructuredJSONField(schema=PersonSchema)
```

Will be serialized as:

```json
{
  "id": 1,
  "title": "Example Person",
  "data": {
    "name": "John",
    "age": 30,
    "friends": [1, 2, 3]  // User IDs
  }
}
```

## ⚠️ Error Handling

One of the key benefits of using `StructuredModelSerializer` is that Pydantic validation errors are automatically translated to DRF-style errors.

### 🚫 Error Response Example

If a client sends invalid data:

```json
{
  "title": "Example",
  "data": {
    "name": 123,  // Should be a string
    "age": "thirty"  // Should be an integer
  }
}
```

The response will contain proper validation errors:

```json
{
  "data": {
    "name": ["String expected"],
    "age": ["Value is not a valid integer"]
  }
}
```

## 🔧 Custom Field Handling

You can still customize field behavior in your serializer:

```python
from rest_framework import serializers
from structured.contrib.rest_framework import StructuredModelSerializer
from .models import MyModel

class MyModelSerializer(StructuredModelSerializer):
    extra_field = serializers.SerializerMethodField()
    
    class Meta:
        model = MyModel
        fields = '__all__'
        
    def get_extra_field(self, obj):
        return f"Name: {obj.structured_data.name}, Age: {obj.structured_data.age}"
```

## 🖥️ Working with Views

You can use the serializer with any DRF view type:

### 📦 ViewSet Example

```python
from rest_framework import viewsets
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
```

### 🔄 Function-Based View Example

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MyModel
from .serializers import MyModelSerializer

@api_view(['GET'])
def get_my_models(request):
    models = MyModel.objects.all()
    serializer = MyModelSerializer(models, many=True)
    return Response(serializer.data)
```

## 💡 Best Practices

1. **📁 Serializer Organization**:
   - Keep your serializers in a separate `serializers.py` file
   - Follow DRF conventions for clarity and maintainability
   - Reuse serializers for similar models or schemas

2. **✅ Validation**:
   - Use Pydantic validators in your schema for field-specific validation
   - Use DRF serializer validation for cross-field validation
   - Provide clear error messages in all validators

3. **⚡ Performance**:
   - Enable caching to optimize query performance with related fields
   - Use appropriate database indexing for fields used in filtering
   - Consider pagination for endpoints returning multiple items

4. **🔒 Security**:
   - Be careful with nested writable serializers and permissions
   - Validate data at both the schema and serializer levels
   - Use appropriate authentication and permission classes

## ❓ Common Issues and Solutions

1. **🚫 Schema Validation Errors**:
   - Ensure your schema is correctly defined with proper types
   - Remember that DRF may convert some types (e.g., strings to numbers)
   - Check the exact error message to identify the issue

2. **🔗 Related Fields Not Working**:
   - Verify that the model exists and is correctly referenced
   - Check that the IDs being passed actually exist in the database
   - Make sure you're using the correct field type (ForeignKey vs QuerySet)

3. **🐢 Performance Issues**:
   - Enable caching for better performance with related fields
   - Use `select_related()` and `prefetch_related()` in your querysets
   - Optimize database queries by selecting only needed fields

## 🔄 Next Steps

After mastering REST Framework integration, you might want to explore:
- [⚡ Caching](../Caching/README.md) for optimizing API performance
- [🔗 Relationships](../Relationships/README.md) for more complex data structures
- [🧰 Admin Integration](../Admin%20Integration/README.md) for managing data through the admin interface 