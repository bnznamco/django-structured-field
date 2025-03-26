# 🧰 Admin Integration

This guide explains how to integrate Django Structured JSON Field with the Django admin interface.

## 🚀 Basic Setup

### 1️⃣ Configure URLs

First, include the structured URLs in your `urls.py` to enable the autocomplete search feature:

```python
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('structured.urls')),  # Required for autocomplete search
]
```

### 2️⃣ Register Your Model

Register your model in `admin.py`:

```python
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    pass
```

The `StructuredJSONField` will automatically use a custom JSON editor in the admin interface. This editor provides:

- A structured form for editing JSON data
- Autocomplete for related fields (ForeignKey and QuerySet)
- Validation against your schema

## 🔧 JSON Editor Features

The JSON editor in the admin interface provides several features:

1. **✅ Schema-based Validation**: Ensures data conforms to your Pydantic schema
2. **🔍 Related Object Search**: Autocomplete for foreign keys and querysets
3. **📦 Nested Data Editing**: Support for nested schema objects
4. **🖌️ User-friendly Interface**: Visual editor for JSON data

## 📝 Working with Structured Data in Admin

### 🧩 Simple Data

You can create and edit simple structured data directly in the admin:

```python
# In your model
class MySchema(BaseModel):
    name: str
    age: int = None

class MyModel(models.Model):
    title = models.CharField(max_length=100)
    structured_data = StructuredJSONField(schema=MySchema)
```

In the admin, you'll be able to edit this as:

```json
{
  "name": "John Doe",
  "age": 30
}
```

### 📦 Nested Data

You can also work with nested structured data:

```python
# In your model
class ChildSchema(BaseModel):
    name: str
    age: int = None

class ParentSchema(BaseModel):
    name: str
    age: int = None
    child: ChildSchema = None

class MyModel(models.Model):
    title = models.CharField(max_length=100)
    structured_data = StructuredJSONField(schema=ParentSchema)
```

In the admin, you'll be able to edit this as:

```json
{
  "name": "Parent",
  "age": 40,
  "child": {
    "name": "Child",
    "age": 10
  }
}
```

### 🔑 Foreign Key Fields

For foreign key fields:

```python
# In your model
class MySchema(BaseModel):
    name: str
    age: int = None
    fk_field: SomeModel = None  # Foreign key reference

class MyModel(models.Model):
    title = models.CharField(max_length=100)
    structured_data = StructuredJSONField(schema=MySchema)
```

In the admin, you can use the ID of the related model:

```json
{
  "name": "John",
  "age": 30,
  "fk_field": 1  # ID of the related SomeModel instance
}
```

The admin interface will display this as a searchable dropdown.

### 🔀 QuerySet Fields

For QuerySet fields:

```python
# In your model
class MySchema(BaseModel):
    name: str
    age: int = None
    qs_field: QuerySet[SomeModel]  # Multiple related objects

class MyModel(models.Model):
    title = models.CharField(max_length=100)
    structured_data = StructuredJSONField(schema=MySchema)
```

In the admin, you can use a list of IDs:

```json
{
  "name": "John",
  "age": 30,
  "qs_field": [1, 2, 3]  # IDs of related SomeModel instances
}
```

The admin interface will display this as a searchable multi-select field.

## 🎨 Customizing the Admin Display

### 📋 List Display

You can display structured data fields in the list view:

```python
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_structured_name', 'get_structured_age']
    
    def get_structured_name(self, obj):
        return obj.structured_data.name if obj.structured_data else None
    get_structured_name.short_description = 'Name'
    
    def get_structured_age(self, obj):
        return obj.structured_data.age if obj.structured_data else None
    get_structured_age.short_description = 'Age'
```

### 🔍 Search Fields

You can search within structured data fields:

```python
@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    search_fields = ['title', 'structured_data__name']  # Search by name in structured data
```

Note that search on JSON fields may have limitations depending on your database.

## 💡 Best Practices

1. **📁 Field Organization**:
   - Keep related fields grouped in your schema
   - Use descriptive field names
   - Consider the admin user experience when designing your schema

2. **✅ Validation**:
   - Use Pydantic validators in your schema for custom validation
   - Handle potential empty or invalid values gracefully

3. **🔄 Default Values**:
   - Provide sensible defaults for all fields
   - Use initialization functions for complex defaults

4. **🔗 Related Objects**:
   - Use descriptive labels for related object fields
   - Consider using pre-filtered querysets for large relationships

## ❓ Common Issues and Solutions

1. **🔍 Autocomplete Not Working**:
   - Ensure that `structured.urls` is included in your URLs
   - Check browser console for JavaScript errors
   - Verify that the related model is correctly registered

2. **⚠️ Validation Errors**:
   - Check the JSON format in the editor
   - Ensure all required fields have values
   - Verify that related object IDs exist

3. **⚡ Performance**:
   - Limit the number of related objects shown in dropdowns
   - Use appropriate indexing on related model fields
   - Enable caching for better performance

## 🔄 Next Steps

After mastering admin integration, you might want to explore:
- [🌍 REST Framework Integration](../REST%20Framework%20Integration/README.md) for API endpoints
- [⚡ Caching](../Caching/README.md) for optimizing admin performance
- [🔗 Relationships](../Relationships/README.md) for more complex data structures 