<div class="logo">
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">

  <!-- Main container (Magenta red background) -->
  <rect x="50" y="50" width="100" height="100" rx="10" ry="10" fill="#E6375A" />
  
  <!-- JSON brackets (styled as "{" and "}") -->
  <path d="M70,70 C80,70 80,85 70,85 C80,85 80,100 70,100" 
        fill="none" stroke="#7C4DFF" stroke-width="8" stroke-linecap="round" />
  <path d="M130,70 C120,70 120,85 130,85 C120,85 120,100 130,100" 
        fill="none" stroke="#7C4DFF" stroke-width="8" stroke-linecap="round" />
  
  <!-- Structured data lines (representing JSON structure) -->
  <line x1="80" y1="115" x2="120" y2="115" stroke="#00E5FF" stroke-width="5" />
  <line x1="80" y1="130" x2="105" y2="130" stroke="#00E5FF" stroke-width="5" />
  
  <!-- Visual elements showing structure -->
  <circle cx="100" cy="85" r="6" fill="#FFD600" />
  <circle cx="85" cy="100" r="6" fill="#FFD600" />
  <circle cx="115" cy="100" r="6" fill="#FFD600" />
  
  <!-- Connect the dots to show relationships -->
  <line x1="100" y1="85" x2="85" y2="100" stroke="#FFD600" stroke-width="2" />
  <line x1="100" y1="85" x2="115" y2="100" stroke="#FFD600" stroke-width="2" />
</svg>
</div>
<h3 style="text-align: center;">Django Structured JSON Field 🧪</h3><br>


## ✨ Features

<!-- Highlight some of the features your module provide here -->

- 📐 &nbsp;Define the structure of a JSON field using Pydantic models
- ✅ &nbsp;Validate the JSON field against the defined structure
- 🔗 &nbsp;Use relationships between models inside the JSON field 
- 🚀 &nbsp;Easily integrate with Django Rest Framework serializers
- 🎛️ &nbsp;Admin editor for the JSON field with autocomplete search for related models 👀


## 🛠️ Quick Setup

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
from pydantic import BaseModel
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

For more advanced usage examples and features, check out the [documentation](docs/README.md).