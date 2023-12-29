# Django Structured JSON Field [![PyPI](https://img.shields.io/pypi/v/django-structured-field?style=flat-square)](https://pypi.org/project/django-structured-field) ![Codecov](https://img.shields.io/codecov/c/github/lotrekagency/django-structured-field?style=flat-square) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/lotrekagency/django-structured-field/%20%F0%9F%A7%AA%20Test%20and%20Coverage?style=flat-square) [![GitHub](https://img.shields.io/github/license/lotrekagency/django-structured-field?style=flat-square)](./LICENSE)

This is a Django field that allows you to declare the structure of a JSON field and validate it.

## Installation

```bash
pip install django-structured-field
```

## Usage

```python
from django.db import models
from structured.fields import StructuredJSONField
from structured.pydantic.models import BaseModel

# Define this schema as you would do with a Pydantic model
class MySchema(BaseModel):
    name: str
    age: int = None

# Create a model with a StructuredJSONField with the schema you defined
class MyModel(models.Model):
    structured_data = StructuredJSONField(schema=MySchema, default=dict)

```

## Relationships

This field supports relationships between models, you can define them in your schema and they will be treated as normal django relationships. It also supports recursive schemas.

### Recursion

You can define recursive schemas by declaring the attribute type as a string:

```python
class MySchema(BaseModel):
    name: str
    age: int = None
    parent: 'MySchema' = None
```

### Foreign Keys

You can also define model relationships in your schema:

```python
class MySchema(BaseModel):
    name: str
    age: int = None
    parent: 'MyModel' = None
```

This will treat the parent field as a normal django ForeignKey.

### ManyToMany

If you need a ManyToMany relationship, you can use the `ManyToMany` field:

```python
from structured.pydantic.fields import QuerySet

class MySchema(BaseModel):
    name: str
    age: int = None
    parents: QuerySet['MyModel']
```

### Cache

To prevent the field from making multiple identical queries a caching technique is used. The cache is still a work in progress, please open an issue if you find any problem.


## Contributing

The project is open to contributions, just open an issue or a PR.

### Running tests

```bash
pip install -r requirements-dev.txt
make test
```

### Running test app
    
```bash
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
