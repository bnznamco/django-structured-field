
# Quick Start guide


Here's a quick start guide to help you get started with the Django Structured JSON Field.

### 📋 Prerequisites

- 🐍 Python >=3.8
- 🎯 Django >=4.2
- 📦 Pydantic >=2.0

### 📥 Installation

1. Create and activate a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. Install the required packages:

```bash
pip install django>=4.2
pip install django-structured-json-field
```

### 🚀 Basic Usage

1. Create a new Django project (if you haven't already):

```bash
django-admin startproject myproject
cd myproject
```

2. Add `structured` to your project's `INSTALLED_APPS`:

```python
# myproject/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'structured',  # Add this line
]
```

3. Create a basic model using the structured field:

```python
# myapp/models.py
from django.db import models
from structured.pydantic.models import BaseModel
from structured.fields import StructuredJSONField

class UserProfile(BaseModel):
    name: str
    age: int
    email: str

class User(models.Model):
    profile = StructuredJSONField(model=UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.profile.name
```

4. Create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Run the development server:

```bash
python manage.py runserver
```

### 💡 Additional Tips

- ✅ The structured field will automatically validate your JSON data against the Pydantic model
- 🔄 You can use complex nested models and relationships
- 🎛️ The admin interface provides a user-friendly editor for your structured fields
- 🌐 For API development, the field integrates seamlessly with Django REST Framework

For more advanced usage examples and features, check out the [How to](../How%20to/README.md).