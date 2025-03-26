# ⚙️ Settings Configuration

This guide explains how to configure Django Structured JSON Field through Django settings.

## 📋 Overview

The Django Structured JSON Field can be configured through the `STRUCTURED_FIELD` setting in your Django settings file. This allows you to customize behavior like caching to match your application's needs.

## 🚀 Basic Configuration

Add the following to your `settings.py`:

```python
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': True,  # Default is True
        'SHARED': False   # Default is False, experimental feature
    }
}
```

## 🔧 Available Settings

Currently, the package supports the following settings:

### 🗄️ Cache Settings

```python
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': True,   # Enable/disable caching (default: True)
        'SHARED': False    # Enable thread-shared cache (experimental, default: False)
    }
}
```

## 📝 Settings Explained

### 🗄️ Cache Settings

#### ENABLED

Controls whether the caching mechanism is enabled or disabled:

- `True` (default): Enables caching, which optimizes queries especially for related fields
- `False`: Disables caching, which may be useful for debugging or testing

When caching is enabled, the field maintains an internal cache of related objects (from `ForeignKey` and `QuerySet` fields), reducing the number of database queries needed when accessing these objects.

#### SHARED

Controls whether the cache is shared between instances:

- `False` (default): Each field instance maintains its own cache
- `True` (experimental): Cache is shared across all instances, providing maximum optimization but with potential side effects

The shared cache is marked as experimental because it uses a global cache that's shared across threads, which may lead to unexpected behavior in multi-threaded environments.

## 🔄 Environment-Specific Configurations

### 🛠️ Development Settings

For development, you might want to disable caching to make it easier to debug:

```python
# settings/development.py
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': False  # Disable cache for easier debugging
    }
}
```

### 🧪 Testing Settings

For testing, you might want to test different cache configurations:

```python
# settings/test.py
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': True,  # Test with cache enabled
        'SHARED': False   # Standard cache mode
    }
}
```

### 🌐 Production Settings

For production, the default settings are generally recommended:

```python
# settings/production.py
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': True,  # Enable cache for performance
        'SHARED': False   # Use standard cache mode
    }
}
```

## 🔍 Testing Different Cache Modes

Based on the test files, you can test your application with different cache modes to measure performance and correctness:

### Testing with Cache Disabled

```python
from django.test import override_settings

@override_settings(STRUCTURED_FIELD={'CACHE': {'ENABLED': False}})
def test_without_cache():
    # Test code here
    pass
```

### Testing with Standard Cache

```python
from django.test import override_settings

@override_settings(STRUCTURED_FIELD={'CACHE': {'ENABLED': True, 'SHARED': False}})
def test_with_standard_cache():
    # Test code here
    pass
```

### Testing with Shared Cache

```python
from django.test import override_settings

@override_settings(STRUCTURED_FIELD={'CACHE': {'ENABLED': True, 'SHARED': True}})
def test_with_shared_cache():
    # Test code here
    pass
```

## 📋 Best Practices

1. **Cache Configuration**:
   - Keep caching enabled in production for performance benefits
   - Test thoroughly with both cache enabled and disabled
   - Use the shared cache option only after extensive testing

2. **Testing**:
   - Use Django's `override_settings` to test different cache configurations
   - Measure query counts with different cache settings
   - Verify behavior correctness with all cache configurations

3. **Deployment**:
   - Document your cache settings in your deployment configuration
   - Monitor performance in production
   - Consider adjusting settings based on real-world performance data

## ❓ Common Issues and Solutions

1. **Performance Issues**:
   - If experiencing slow performance with relationships, ensure caching is enabled
   - If memory usage is high, consider if shared cache might be contributing
   - Use Django Debug Toolbar or similar tools to monitor query counts

2. **Unexpected Behavior**:
   - If you notice unexpected results, try disabling the cache to see if caching is the cause
   - Be particularly careful with the shared cache in multi-threaded environments
   - Consider flush/clearing cache between test runs in your test suite

## 🔄 Next Steps

After configuring settings, you might want to explore:
- [⚡ Caching](../Caching) for more details on how caching works
- [🔗 Relationships](../Relationships) for working with related models
- [🌐 REST Framework Integration](../REST%20Framework%20Integration) for API configuration

## 📝 Complete Configuration Example
Here's a complete example with all available settings:
```python
STRUCTURED_FIELD = {
    'CACHE': {
        'ENABLED': True,  # Enable cache for performance (default)
        'SHARED': False   # Use standard cache mode (default, recommended)
    }
}
``` 