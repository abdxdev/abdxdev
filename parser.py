import re


def parse(string) -> dict:
    """
    Parse a string containing a description and optional marker codes.
    
    This function parses strings in the format "description: marker1 marker2..." where:
    - Everything before the colon is considered the description
    - After the colon, there can be various markers like:
      - Bare numbers (e.g., ":23") set a "number" key
      - Letter markers (e.g., ":p") set that key to True
      - Letter markers with numbers (e.g., ":p3") set that key to the number
    - Multiple markers can be separated by colons (e.g., ":p3:s5")
    
    If the string doesn't follow this format (lacks a colon or has spaces in marker part),
    it is considered not parsable.
    
    Args:
        string (str): The input string to parse
        
    Returns:
        dict: A dictionary containing:
            - "is_parsable" (bool): Whether the string follows the expected format
            - "description" (str): The description part of the string
            - Additional keys for any markers found in the string
    """
    result = {
        "is_parsable": False,
        "description": string,
    }
    
    if ":" not in string:
        return result
    
    if string.rstrip().endswith(":"):
        result["is_parsable"] = True
        result["description"] = string.rstrip().rstrip(":").strip()
        return result
    
    parts = string.split(":")
    if len(parts) < 2:
        return result
    
    description = parts[0]
    marker_parts = parts[1:]
    for part in marker_parts:
        if " " in part and part.strip():
            return result
    
    result["is_parsable"] = True
    result["description"] = description.strip()
    for part in marker_parts:
        part = part.strip()
        if not part:
            continue
        if part.isdigit():
            result["number"] = int(part)
            continue
    
        match = re.match(r"^([a-zA-Z]+)(\d+)?$", part)
        if match:
            marker, value = match.groups()
            if value:
                result[marker] = int(value)
            else:
                result[marker] = True
    
    return result


def assert_parse(string, expected):
    result = parse(string)
    result_keys = result.keys()
    expected_keys = expected.keys()
    assert len(result_keys) == len(expected_keys), f"Expected {len(expected_keys)} keys but got {len(result_keys)}"
    assert all(key in result_keys for key in expected_keys), f"Expected keys {expected_keys} but got {result_keys}"
    for key, value in expected.items():
        assert result.get(key) == value, f"Expected {key} to be {value} but got {result.get(key)}"


if __name__ == "__main__":
    test_cases = [
        # Basic cases with proper format
        (
            "The quick brown fox jumps over the lazy dog :",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
            },
        ),
        (
            "The quick brown fox jumps over the lazy dog : ",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
            },
        ),
        # Case without a colon - not parsable
        (
            "The quick brown fox jumps over the lazy dog",
            {
                "is_parsable": False,
                "description": "The quick brown fox jumps over the lazy dog",
            },
        ),
        # Cases with colon in the middle - not parsable in the expected way
        (
            "The quick brown fox :jumps over the lazy dog",
            {
                "is_parsable": False,
                "description": "The quick brown fox :jumps over the lazy dog",
            },
        ),
        (
            "The quick brown fox : jumps over the lazy dog",
            {
                "is_parsable": False,
                "description": "The quick brown fox : jumps over the lazy dog",
            },
        ),
        # Cases with markers after colon
        (
            "The quick brown fox jumps over the lazy dog :p3",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
                "p": 3,
            },
        ),
        (
            "The quick brown fox jumps over the lazy dog :p3:s5",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
                "p": 3,
                "s": 5,
            },
        ),
        (
            "The quick brown fox jumps over the lazy dog :s5",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
                "s": 5,
            },
        ),
        (
            "The quick brown fox jumps over the lazy dog :p",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
                "p": True,
            },
        ),
        (
            "The quick brown fox jumps over the lazy dog :s",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
                "s": True,
            },
        ),
        # Case with only a number after colon - no letter marker
        (
            "The quick brown fox jumps over the lazy dog :23",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
                "number": 23,
            },
        ),
        # Cases with more complex marker patterns
        (
            "The quick brown fox jumps over the lazy dog :ps",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
                "ps": True,
            },
        ),
        (
            "The quick brown fox jumps over the lazy dog :pss5:p3",
            {
                "is_parsable": True,
                "description": "The quick brown fox jumps over the lazy dog",
                "pss": 5,
                "p": 3,
            },
        ),
        # Cases with colons in different positions (these test how the middle colons are handled)
        (
            "The :p3 quick brown :p3fox jumps over:p3 the lazy dog",
            {
                "is_parsable": False,
                "description": "The :p3 quick brown :p3fox jumps over:p3 the lazy dog",
            },
        ),
        (
            "The :p3:s5 quick brown fox :p3:s5jumps over:p3:s5 the lazy dog",
            {
                "is_parsable": False,
                "description": "The :p3:s5 quick brown fox :p3:s5jumps over:p3:s5 the lazy dog",
            },
        ),
        (
            "The :s5 quick brown :s5fox jumps over:s5 the lazy dog",
            {
                "is_parsable": False,
                "description": "The :s5 quick brown :s5fox jumps over:s5 the lazy dog",
            },
        ),
        (
            "The :p quick brown :pfox jumps over:p the lazy dog",
            {
                "is_parsable": False,
                "description": "The :p quick brown :pfox jumps over:p the lazy dog",
            },
        ),
        (
            "The :s quick brown :sfox jumps over:s the lazy dog",
            {
                "is_parsable": False,
                "description": "The :s quick brown :sfox jumps over:s the lazy dog",
            },
        ),
        (
            "The :23 quick brown :23fox jumps over:23 the lazy dog",
            {
                "is_parsable": False,
                "description": "The :23 quick brown :23fox jumps over:23 the lazy dog",
            },
        ),
        (
            "The :ps quick brown :psfox jumps over:ps the lazy dog",
            {
                "is_parsable": False,
                "description": "The :ps quick brown :psfox jumps over:ps the lazy dog",
            },
        ),
        (
            "The :pss5:p3 quick brown fox :pss5:p3jumps over:pss5:p3 the lazy dog",
            {
                "is_parsable": False,
                "description": "The :pss5:p3 quick brown fox :pss5:p3jumps over:pss5:p3 the lazy dog",
            },
        ),
    ]
    for string, expected in test_cases:
        assert_parse(string, expected)
    print("All tests passed!")
