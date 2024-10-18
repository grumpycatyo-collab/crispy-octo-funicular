class CustomSerializer:
    @staticmethod
    def serialize(data, indent=2):
        def serialize_with_indent(obj, level=0):
            base_indent = " " * (level * indent)
            inner_indent = " " * ((level + 1) * indent)

            if isinstance(obj, dict):
                items = []
                for k, v in obj.items():
                    items.append(f"{inner_indent}{k}: {serialize_with_indent(v, level + 1)}")
                return "{\n" + "\n".join(items) + "\n" + base_indent + "}"

            elif isinstance(obj, list):
                items = [f"{inner_indent}{serialize_with_indent(item, level + 1)}" for item in obj]
                return "[\n" + "\n".join(items) + f"\n{base_indent}]"

            else:
                return str(obj)

        return f"CUSTOM_FORMAT:\n{serialize_with_indent(data)}"

    @staticmethod
    def deserialize(data):
        if data.startswith("CUSTOM_FORMAT:"):
            return eval(data[13:])
        raise ValueError("Invalid custom format")

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