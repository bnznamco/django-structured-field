# Django Structured JSON Field [![PyPI](https://img.shields.io/pypi/v/django-structured-json-field?style=flat-square)](https://pypi.org/project/django-structured-json-field) ![Codecov](https://img.shields.io/codecov/c/github/bnznamco/django-structured-field?style=flat-square&logo=codecov&logoSize=auto&cacheSeconds=0) ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/lotrekagency/django-structured-field/ci.yml?style=flat-square) [![GitHub](https://img.shields.io/github/license/lotrekagency/django-structured-field?style=flat-square)](./LICENSE) [![Docs](https://img.shields.io/badge/docs-online-brightgreen?style=flat-square)](https://bnznamco.github.io/django-structured-field/)


<br>
<br>
<div align="center">
<svg width="330" height="330" viewBox="0 0 330 330" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M103.308 0H154.334L155.249 3.8483C156.883 10.7201 154.771 17.9439 149.692 22.8532L86.5743 83.8711C80.0668 90.1621 79.8913 100.537 86.1822 107.045C92.4732 113.552 102.848 113.728 109.356 107.437L152.337 65.8856C158.677 59.7571 169.277 62.8564 171.316 71.4349C172.262 75.4148 170.999 79.5962 168.008 82.3867L91.4196 153.838C86.9138 158.042 80.4982 159.503 74.6162 157.666L69.8424 156.175C66.4627 155.119 64.1183 152.159 62.8493 148.853L52.118 120.9C50.1435 115.757 50.378 110.027 52.7664 105.062L103.308 0ZM25.1937 2.98025L0.129341 27.1957C0.0437515 28.119 0 29.0544 0 30V95.1742L45.785 0H30C29.182 0 28.3717 0.0327355 27.5703 0.0969673C26.9044 1.1245 26.112 2.09304 25.1937 2.98025ZM176.567 7.04853L174.892 0H300C316.569 0 330 13.4315 330 30V100.18C330 118.477 312.255 131.525 294.79 126.07L288.979 124.254C284.545 122.869 281.014 119.49 279.435 115.12C274.572 101.657 259.716 94.6856 246.253 99.5485C245.846 99.6958 245.436 99.8445 245.025 99.9939C237.502 102.727 229.438 105.656 221.867 103.291L209.702 99.4907C206.271 98.4188 202.528 99.2714 199.899 101.724L102.679 192.423C100.05 194.876 98.9399 198.55 99.7714 202.048L107.98 236.579C109.009 240.906 108.629 245.475 108.248 250.045C107.88 254.472 107.511 258.901 108.423 263.112C109.047 265.992 110.455 268.739 112.653 271.014C115.012 273.456 117.374 276.095 118.159 279.398L121.408 293.062C125.888 311.91 111.595 330 92.2209 330H89C72.4315 330 59 316.569 59 300V226.5C59 210.208 45.7924 197 29.5 197C13.2076 197 0 183.792 0 167.5V155.311L2.30329 156.031C7.88385 157.774 12.3606 161.974 14.456 167.432C19.5863 180.795 34.5784 187.469 47.9418 182.339C48.042 182.301 48.1419 182.262 48.2414 182.222C48.4814 182.127 48.7221 182.031 48.9634 181.934C56.5975 178.891 64.8963 175.583 72.6945 178.019L83.7186 181.462C87.1502 182.534 90.8931 181.682 93.5218 179.229L190.742 88.5297C193.371 86.0773 194.481 82.4025 193.649 78.9049L185.38 44.1183C184.487 40.3608 185.026 36.4669 185.564 32.5772C185.814 30.7706 186.064 28.9649 186.171 27.1743C186.433 22.7542 184.914 18.2424 181.594 14.808C179.418 12.5573 177.291 10.0941 176.567 7.04853ZM106.826 95.0072C106.923 99.5553 103.315 103.321 98.7669 103.418C94.2188 103.516 90.453 99.9074 90.3557 95.3593C90.2585 90.8112 93.8667 87.0454 98.4147 86.9482C102.963 86.8509 106.729 90.4591 106.826 95.0072ZM170.52 34.1428C175.068 34.0456 178.676 30.2798 178.579 25.7317C178.482 21.1836 174.716 17.5754 170.168 17.6727C165.62 17.7699 162.012 21.5357 162.109 26.0838C162.206 30.6319 165.972 34.24 170.52 34.1428ZM180.19 322.76C181.53 326.25 178.953 330 175.214 330H172.815C172.109 330 171.407 329.893 170.734 329.683L165.355 328.002C155.253 324.847 147.561 316.602 145.113 306.305L140.588 287.268C138.136 276.957 141.307 266.118 148.93 258.754L207.694 201.98C214.203 195.691 214.382 185.316 208.093 178.807C201.804 172.297 191.429 172.118 184.919 178.407L144.751 217.215C137.276 224.437 124.782 220.782 122.378 210.67C121.263 205.978 122.752 201.048 126.279 197.758L202.117 127.007C206.551 122.87 212.865 121.432 218.653 123.24L223.206 124.662C226.883 125.811 229.372 129.107 230.681 132.731L239.046 155.889C241.783 163.466 241.357 171.826 237.865 179.086L180.322 298.701C177.507 304.553 177.086 310.937 178.67 316.746C178.928 318.761 179.429 320.778 180.19 322.76ZM307.043 321.936C301.489 327.118 294.175 330 286.579 330H250.443C243.246 330 236.793 325.565 234.213 318.846C232.497 314.376 232.701 309.395 234.777 305.08L294.726 180.463C297.759 174.157 298.013 167.233 295.973 161.078C295.813 160.52 295.633 159.965 295.433 159.412C293.397 153.774 298.692 148.242 304.414 150.029L318.846 154.537C323.814 156.089 327.597 160.144 328.801 165.208L329.464 167.994C329.82 169.493 330 171.029 330 172.57V211.248C330 219.38 326.698 227.164 320.851 232.817L269.074 282.871C262.567 289.162 262.391 299.537 268.682 306.045C274.973 312.552 285.348 312.728 291.856 306.437L311.208 287.729C318.244 280.927 330 285.913 330 295.7C330 298.774 328.724 301.71 326.476 303.807L307.043 321.936ZM328.915 328.884C328.487 329.283 328.77 330 329.355 330C329.711 330 330 329.711 330 329.355C330 328.791 329.327 328.499 328.915 328.884ZM124.892 250.921C129.147 250.832 132.716 253.985 133.237 258.116C133.264 258.395 133.279 258.678 133.279 258.964C133.279 262.819 130.711 266.076 127.193 267.116C126.568 267.282 125.914 267.377 125.239 267.392C120.69 267.487 116.926 263.878 116.83 259.33C116.734 254.782 120.343 251.017 124.892 250.921ZM281.267 302.418C285.815 302.321 289.423 298.555 289.326 294.007C289.229 289.459 285.463 285.851 280.915 285.948C276.367 286.045 272.758 289.811 272.856 294.359C272.953 298.907 276.719 302.516 281.267 302.418ZM197.013 198.138C201.561 198.042 205.171 194.278 205.075 189.729C204.979 185.181 201.214 181.572 196.666 181.668C192.118 181.764 188.509 185.528 188.604 190.077C188.7 194.625 192.465 198.234 197.013 198.138ZM280.5 86C301.211 86 318 69.2107 318 48.5C318 27.7893 301.211 11 280.5 11C259.789 11 243 27.7893 243 48.5C243 69.2107 259.789 86 280.5 86Z" fill="#D9D9D9"/>
<circle cx="280.5" cy="48.5" r="21.5" fill="#e6375a"/>
</svg>
</div>

<br>
<br>
<br>
<br>



This is a Django field that allows you to declare the structure of a JSON field and validate it.

## Features

- Define the structure of a JSON field using Pydantic models
- Validate the JSON field against the defined structure
- Use relationships between models inside the JSON field 🤯
- Easily integrate with Django Rest Framework serializers
- Admin editor for the JSON field with autocomplete search for related models 👀


## Documentation

Check out our [documentation](https://bnznamco.github.io/django-structured-field/) for detailed guides and examples on:

- Installation and basic usage
- Working with relationships
- Admin integration
- REST Framework integration
- Caching
- Settings configuration



## Installation

```bash
pip install django-structured-json-field
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

def init_data():
    return MySchema(name='')

# Create a model with a StructuredJSONField with the schema you defined
class MyModel(models.Model):
    structured_data = StructuredJSONField(schema=MySchema, default=init_data)

```

## Relationships

This field supports relationships between models, you can define them in your schema and they will be treated as normal django relationships. It also supports recursive schemas.

### Recursion

You can define recursive schemas by declaring the attribute type as a string:

```python
from typing import Optional, List

class MySchema(BaseModel):
    name: str
    age: int = None
    parent: Optional['MySchema'] = None
    relateds: List['MySchema'] = []
```

### Foreign Keys

You can also define model relationships in your schema:

```python
from structured.pydantic.fields import ForeignKey

class MySchema(BaseModel):
    name: str
    age: int = None
    fk_field: ForeignKey['MyModel'] = None
```

This will treat the parent field as a normal django ForeignKey.

#### Tip:

You can omit the `ForeignKey` field and just use the model class as the type annotation:

```python
class MySchema(BaseModel):
    name: str
    age: int = None
    fk_field: MyModel = None
```

the field will still be treated as a ForeignKey if the type annotation is a subclass of django `models.Model`.

### ManyToMany

If you need a ManyToMany relationship, you can use the `QuerySet` field:

```python
from structured.pydantic.fields import QuerySet

class MySchema(BaseModel):
    name: str
    age: int = None
    parents: QuerySet['MyModel']
```

`QuerySet` fields will generate a django object manager that will allow you to query the related objects as you would do with a normal django `QuerySet`.

```python
instance = MySchema(name='test', age=10, parents=MyModel.objects.all())
# You can filter the queryset
instance.parents.filter(name='test')
# You can count the queryset
instance.parents.count()
# You can get the first element of the queryset, etc...
instance.parents.first()
```

### Admin integration

The field is integrated with the Django admin, you can use the autocomplete search to select the related models. To allow the autocomplete search you need to include structured.urls in your urls.py file:

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('structured.urls')),
]
```

### Rest Framework integration

You can easily integrate structured fields with Django Rest Framework serializers, just use the `StructuredModelSerializer` as the base class for your serializer:

```python
from rest_framework import serializers
from structured.contrib.rest_framework import StructuredModelSerializer

class MyModelSerializer(StructuredModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'
```

Errors generated by pydantic validation will be automatically translated to DRF errors.


### Cache

To prevent the field from making multiple identical queries a caching technique is used. The cache is still a work in progress, please open an issue if you find any problem.
Actually the cache covers all the relations inside a StructuredJSONField, optimizing the queries during the serialization process.

#### Cache engine progress:

- [x] Shared cache between `ForeignKey` fields and `QuerySet` fields
- [x] Shared cache through nested schemas
- [x] Shared cache through nested lists of schemas
- [ ] Shared cache between all `StructuredJSONFields` in the same instance
- [ ] Shared cache between multiple instances of the same model
- [ ] Cache invalidation mechanism

## Settings

You can manage structured field behaviour modifying the `STRUCTURED_FIELD` setting in your `settings.py` file. Here a list of the available settings and their default values:

```python
STRUCTURED_FIELD = {
    'CACHE':{
        'ENABLED': True,
        'SHARED': False # ⚠️ EXPERIMENTAL: this enables a thread-shared cache, it's not recommended to use it in production.
    },
}
```

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
