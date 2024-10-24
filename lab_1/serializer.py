from typing import Any, Union, Dict, List


class SerializationError(Exception):
    """Custom exception for serialization/deserialization errors"""
    pass


class CustomSerializer:
    """
    A custom serializer that converts Python objects to a string format and back.
    Supports basic types, lists, and dictionaries.
    """

    @staticmethod
    def serialize(data: Any, indent: int = 2) -> str:
        """
        Serialize Python objects into a custom string format.

        Args:
            data: The Python object to serialize
            indent: Number of spaces for indentation

        Returns:
            str: The serialized string representation
        """

        def serialize_with_indent(obj: Any, level: int = 0) -> str:
            base_indent = " " * (level * indent)
            inner_indent = " " * ((level + 1) * indent)

            if isinstance(obj, dict):
                if not obj:
                    return "{}"
                items = []
                for k, v in obj.items():
                    items.append(f"{inner_indent}{k}: {serialize_with_indent(v, level + 1)}")
                return "{\n" + "\n".join(items) + "\n" + base_indent + "}"

            elif isinstance(obj, list):
                if not obj:
                    return "[]"
                items = [f"{inner_indent}{serialize_with_indent(item, level + 1)}" for item in obj]
                return "[\n" + "\n".join(items) + f"\n{base_indent}]"

            elif isinstance(obj, (int, float)):
                return str(obj)
            elif isinstance(obj, bool):
                return str(obj).lower()
            elif isinstance(obj, str):
                return f'"{obj}"'
            elif obj is None:
                return "null"
            else:
                raise SerializationError(f"Unsupported type: {type(obj)}")

        try:
            return f"CUSTOM_FORMAT:\n{serialize_with_indent(data)}"
        except Exception as e:
            raise SerializationError(f"Serialization failed: {str(e)}")

    @staticmethod
    def deserialize(data: str) -> Any:
        """
        Deserialize the custom string format back into Python objects.

        Args:
            data: The string to deserialize

        Returns:
            The deserialized Python object
        """
        if not isinstance(data, str):
            raise SerializationError("Input must be a string")

        if not data.startswith("CUSTOM_FORMAT:"):
            raise SerializationError("Invalid custom format")

        def parse_value(value_str: str) -> Any:
            value_str = value_str.strip()

            if not value_str:
                return None

            if value_str.startswith('{'):
                return parse_dict(value_str)
            elif value_str.startswith('['):
                return parse_list(value_str)
            elif value_str.startswith('"') and value_str.endswith('"'):
                return value_str[1:-1]
            elif value_str.lower() == 'true':
                return True
            elif value_str.lower() == 'false':
                return False
            elif value_str.lower() == 'null':
                return None
            try:
                if '.' in value_str:
                    return float(value_str)
                return int(value_str)
            except ValueError:
                return value_str

        def parse_dict(dict_str: str) -> Dict:
            result = {}
            content = dict_str.strip('{}')
            if not content:
                return result

            items = [line.strip() for line in content.split('\n') if line.strip()]

            for item in items:
                if ':' in item:
                    key, value = item.split(':', 1)
                    result[key.strip()] = parse_value(value)
            return result

        def parse_list(list_str: str) -> List:
            result = []
            content = list_str.strip('[]')
            if not content:
                return result


            items = [line.strip() for line in content.split('\n') if line.strip()]

            for item in items:
                result.append(parse_value(item))
            return result

        try:
            return parse_value(data[13:].strip())
        except Exception as e:
            raise SerializationError(f"Deserialization failed: {str(e)}")

    @staticmethod
    def validate_format(data: str) -> bool:
        """
        Validate if the input string is in the correct format.

        Args:
            data: The string to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(data, str):
            return False
        if not data.startswith("CUSTOM_FORMAT:"):
            return False
        try:
            CustomSerializer.deserialize(data)
            return True
        except:
            return False


def test_serializer():
    """Test function to verify serializer functionality"""
    serializer = CustomSerializer()


    test_cases = [

        42,
        3.14,
        "Hello, World!",
        True,
        False,
        None,


        [1, 2, 3],
        {"name": "John", "age": 30},


        {
            "person": {
                "name": "John Doe",
                "age": 30,
                "is_active": True,
                "scores": [95, 87, 91],
                "address": {
                    "city": "New York",
                    "zip": "10001"
                }
            }
        }
    ]

    for test_data in test_cases:
        try:

            serialized = serializer.serialize(test_data)
            print(f"\nSerialized:\n{serialized}")


            deserialized = serializer.deserialize(serialized)
            print(f"Deserialized: {deserialized}")

            assert test_data == deserialized, f"Test failed for {test_data}"
            print("Test passed!")

        except Exception as e:
            print(f"Test failed for {test_data}: {str(e)}")

def manual_json_serialize(data, indent=2, level=0):
    if isinstance(data, dict):
        if not data:
            return "{}"
        items = []
        base_indent = " " * (level * indent)
        inner_indent = " " * ((level + 1) * indent)
        for k, v in data.items():
            items.append(f'{inner_indent}"{k}": {manual_json_serialize(v, indent, level + 1)}')
        return "{\n" + ",\n".join(items) + f"\n{base_indent}}}"

    elif isinstance(data, list):
        if not data:
            return "[]"
        items = []
        base_indent = " " * (level * indent)
        inner_indent = " " * ((level + 1) * indent)
        for item in data:
            items.append(f"{inner_indent}{manual_json_serialize(item, indent, level + 1)}")
        return "[\n" + ",\n".join(items) + f"\n{base_indent}]"

    elif isinstance(data, str):
        return f'"{data}"'
    elif isinstance(data, (int, float)):
        return str(data)
    elif data is None:
        return "null"
    else:
        return f'"{str(data)}"'


def manual_xml_serialize(data, root_name="root", indent=2, level=0):
    def create_element(name, value, level):
        base_indent = " " * (level * indent)

        if isinstance(value, dict):
            elements = [f"{base_indent}<{name}>"]
            for k, v in value.items():
                elements.append(create_element(k, v, level + 1))
            elements.append(f"{base_indent}</{name}>")
            return "\n".join(elements)

        elif isinstance(value, list):
            elements = [f"{base_indent}<{name}>"]
            for item in value:
                elements.append(create_element("item", item, level + 1))
            elements.append(f"{base_indent}</{name}>")
            return "\n".join(elements)

        else:
            return f"{base_indent}<{name}>{str(value)}</{name}>"

    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    content = create_element(root_name, data, 0)
    return f"{xml_declaration}\n{content}"