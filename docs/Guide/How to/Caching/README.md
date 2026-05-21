# ⚡ Caching
This guide explains how to work with caching in Django Structured JSON Field.

## 📋 Overview
The field implements a caching mechanism to optimize queries during serialization and prevent multiple identical queries, especially when dealing with relationships such as `ForeignKey` and `QuerySet` fields.

## 🌟 Current Cache Features
- ✅ Shared cache between `ForeignKey` fields and `QuerySet` fields
- ✅ Shared cache through nested schemas
- ✅ Shared cache through nested lists of schemas
- ✅ Cross-row bulk fetch via [🚀 Prefetching Relations](../Prefetching%20Relations/README.md)
- ⏳ Shared cache between all `StructuredJSONFields` in the same instance
- ⏳ Shared cache between multiple instances of the same model
- ⏳ Cache invalidation mechanism

## 🔧 Configuration

### 📌 Basic Settings
Configure caching in your `settings.py`:
```python
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': True,  # Default is True
        'SHARED': False   # ⚠️ EXPERIMENTAL: enables thread-shared cache
    },
}
```

### 🔄 Cache Options
1. **ENABLED**: Enable/disable caching globally (default: `True`)
2. **SHARED**: Enable thread-shared cache (experimental feature, default: `False`)

## 🧠 How Caching Works

The caching system in Django Structured JSON Field is designed to optimize query performance when working with related objects:

1. When a related object is first accessed, it's fetched from the database and stored in the cache
2. Subsequent accesses to the same related object will use the cached version instead of making another database query
3. The cache is maintained during the serialization process, improving performance especially with deeply nested structures

### 🐢 Without Caching (Multiple Queries)

When caching is disabled, each access to a related field requires a separate database query:

```python
# Without caching, this makes 6 separate database queries
instance = TestModel.objects.first()
instance.structured_data.fk_field.name
instance.structured_data.child.fk_field.name
instance.structured_data.child.child.fk_field.name
instance.structured_data.child.child.child.fk_field.name
instance.structured_data.child.child.child.child.fk_field.name
instance.structured_data.child.child.child.child.child.fk_field.name
```

### 🚀 With Caching (Single Query)

When caching is enabled, related objects are fetched with a single optimized query:

```python
# With caching, this makes just 1 database query for all related objects
instance = TestModel.objects.first()
instance.structured_data.fk_field.name
instance.structured_data.child.fk_field.name
instance.structured_data.child.child.fk_field.name
instance.structured_data.child.child.child.fk_field.name
instance.structured_data.child.child.child.child.fk_field.name
instance.structured_data.child.child.child.child.child.fk_field.name
```

## 📊 Cache Performance Benefits

The caching system provides significant performance benefits in several scenarios:

### 1️⃣ Nested Foreign Keys

```python
class ChildSchema(BaseModel):
    name: str
    fk_field: SomeModel = None

class ParentSchema(BaseModel):
    name: str
    child: ChildSchema = None
    fk_field: SomeModel = None
```

When accessing multiple foreign keys in a nested structure, the cache ensures efficient queries.

### 2️⃣ QuerySet Fields

```python
class MySchema(BaseModel):
    name: str
    qs_field: QuerySet[SomeModel]
```

When working with QuerySet fields, the cache ensures the related objects are fetched efficiently.

### 3️⃣ Lists of Nested Schemas

```python
class ChildSchema(BaseModel):
    name: str
    fk_field: SomeModel = None

class ParentSchema(BaseModel):
    name: str
    childs: List[ChildSchema] = []
```

The cache works effectively even with lists of schemas containing relationships.

## 🔄 Cache Behavior in Different Modes

### 🔒 Standard Cache (SHARED=False)

- Cache is maintained per instance
- Optimizes queries within a single instance
- Safe for production use

### 🌐 Shared Cache (SHARED=True)

- Cache is shared across all instances
- Provides maximum optimization but with some risks
- Experimental and not recommended for production without testing

## 💡 Best Practices

1. **⚙️ Cache Configuration**:
   - Keep caching enabled in production for performance benefits
   - Test thoroughly before enabling shared cache in production
   - Consider disabling cache only for debugging purposes

2. **🔍 Query Optimization**:
   - Use appropriate database indexes on related model fields
   - Still use `select_related()` when fetching initial models
   - For relations *inside* the JSON, use [🚀 Prefetching Relations](../Prefetching%20Relations/README.md) — Django's `prefetch_related` syntax works transparently across structured paths
   - Consider query patterns in your application design

3. **🧪 Testing**:
   - Test your application with both cache enabled and disabled
   - Verify behavior with both standard and shared cache
   - Use profiling tools to measure performance improvements

## ❓ Common Issues and Solutions

1. **🔄 Stale Data**:
   - Cache doesn't automatically update when related objects change
   - Refresh objects from database when needed
   - Consider application design to minimize cache staleness

2. **💾 Memory Usage**:
   - Monitor memory consumption with large datasets
   - Be aware of the memory tradeoff for performance
   - Consider clearing cache for very large operations

## 🔧 Testing Different Cache Configurations

You can test different cache configurations by modifying your settings:

```python
# Disable cache entirely (for testing or debugging)
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': False,
    },
}

# Enable standard cache (recommended for production)
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': True,
        'SHARED': False,
    },
}

# Enable shared cache (experimental)
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': True,
        'SHARED': True,
    },
}
```

## 🔄 Next Steps

After understanding caching, you might want to explore:
- [🚀 Prefetching Relations](../Prefetching%20Relations/README.md) for `prefetch_related` across JSON paths
- [🌍 REST Framework Integration](../REST%20Framework%20Integration/README.md) for API optimization
- [🔗 Relationships](../Relationships/README.md) for complex data structures
- [🧰 Admin Integration](../Admin%20Integration/README.md) for admin interface optimization 