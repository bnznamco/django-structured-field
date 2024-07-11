
# test find_and_replace_dict
def test_find_and_replace_dict():
    from structured.utils.replace import find_and_replace_dict

    # test find_and_replace_dict with a simple predicate
    def predicate(key, value):
        if key == "name":
            return "John"
        return value

    obj = {"name": "Jane", "age": 30}
    result = find_and_replace_dict(obj, predicate)
    assert result == {"name": "John", "age": 30}

    # test find_and_replace_dict with a nested predicate
    def predicate(key, value):
        if key == "name":
            return "John"
        if key == "child":
            return find_and_replace_dict(value, predicate)
        return value

    obj = {
        "name": "Jane",
        "age": 30,
        "child": {"name": "Jane", "age": 25},
    }
    result = find_and_replace_dict(obj, predicate)
    assert result == {
        "name": "John",
        "age": 30,
        "child": {"name": "John", "age": 25},
    }
    

