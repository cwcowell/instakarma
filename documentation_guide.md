# reST-Style Python Documentation Guide

## Overview
reStructuredText (reST) is the official documentation format for Python and is particularly well-suited for use with Sphinx documentation generator.

## Basic Structure
```python
"""Short summary.

Detailed description of function/class.

:param name: Parameter description
:type name: str
:returns: Description of return value
:rtype: bool
:raises ValueError: Description of when ValueError is raised
"""
```

## Standard Field Labels

### For Functions
- `:param name:` - Parameter description
- `:type name:` - Parameter type
- `:returns:` - Return value description
- `:rtype:` - Return value type
- `:raises:` - Exceptions that may be raised
- `:example:` - Example usage

### For Classes
- `:ivar name:` - Instance variable description
- `:vartype name:` - Instance variable type
- `:cvar name:` - Class variable description
- `:var name:` - Variable description (generic)

## Code Examples

### Class Documentation
```python
class Rectangle:
    """
    A class to represent a rectangle.

    :param width: The width of the rectangle
    :type width: float
    :param height: The height of the rectangle
    :type height: float
    :ivar width: The width of the rectangle
    :vartype width: float
    :ivar height: The height of the rectangle
    :vartype height: float
    :raises ValueError: If width or height is negative
    """
```

### Method Documentation
```python
def calculate_area(length: float, width: float) -> float:
    """
    Calculate the area of a rectangle.

    :param length: The length of the rectangle
    :type length: float
    :param width: The width of the rectangle
    :type width: float
    :returns: The area of the rectangle
    :rtype: float
    :raises ValueError: If either length or width is negative

    :example:

    >>> calculate_area(2, 3)
    6.0
    """
```

### Property Documentation
```python
@property
def area(self) -> float:
    """
    Calculate the area of the rectangle.

    :returns: The area using width * height
    :rtype: float
    """
```

## Best Practices

### Do's
- Start with a short summary line
- Leave a blank line after the summary
- Use complete sentences with periods
- Include all parameters and their types
- Document all exceptions that may be raised
- Use consistent indentation
- Include examples for complex functionality

### Don'ts
- Don't mix reST with other documentation styles
- Don't skip parameter types
- Don't forget to document raises conditions
- Don't use redundant type information when using type hints
- Don't include implementation details

## Examples by Complexity

### Simple Function
```python
def add(x: int, y: int) -> int:
    """
    Add two numbers together.

    :param x: First number
    :type x: int
    :param y: Second number
    :type y: int
    :returns: The sum of x and y
    :rtype: int
    """
```

### Complex Function
```python
def process_data(data: list[dict], 
                threshold: float = 0.5, 
                normalize: bool = False) -> tuple[list, dict]:
    """
    Process a list of data points according to specified parameters.

    This function analyzes each data point and filters based on the
    threshold value. Data can optionally be normalized before processing.

    :param data: List of dictionaries containing data points
    :type data: list[dict]
    :param threshold: Minimum value to include in results, defaults to 0.5
    :type threshold: float
    :param normalize: Whether to normalize values before processing,
                     defaults to False
    :type normalize: bool
    :returns: Tuple containing processed data and statistics
    :rtype: tuple[list, dict]
    :raises ValueError: If threshold is negative
    :raises KeyError: If data dictionaries are missing required keys
    :raises TypeError: If data is not a list of dictionaries

    :example:

    >>> data = [{'value': 1.0, 'timestamp': '2024-01-01'}]
    >>> process_data(data, threshold=0.8)
    ([{'value': 1.0, 'timestamp': '2024-01-01'}], {'processed': 1})
    """
```

## Sphinx Integration

### Special Directives
- `:note:` - Add a note section
- `:warning:` - Add a warning section
- `:seealso:` - Add a see also section
- `:deprecated:` - Mark as deprecated

Example:
```python
def old_function():
    """
    This is an old function.

    :deprecated: Use `new_function()` instead
    :seealso: `new_function()`
    :note: Will be removed in version 2.0
    """
```

### Cross-Referencing
```python
def new_function():
    """
    New improved function.

    :seealso: :func:`old_function`
    """
```

## IDE Configuration

### PyCharm/IntelliJ Configuration
1. Go to Settings/Preferences
2. Navigate to Tools → Python Integrated Tools
3. Set Docstring Format to "reStructuredText"

### VS Code Configuration
1. Install Python extension
2. Set `"python.pythonPath"` in settings
3. Set `"autoDocstring.docstringFormat"` to "sphinx"

## Common Patterns

### Module Documentation
```python
"""
Module Name
===========

Description of module functionality.

:author: Author Name
:contact: author@email.com
:copyright: 2024, Author
:license: MIT
"""
```

### Package Documentation
```python
"""
Package Name
===========

Description of package functionality.

Modules
-------
module1
    Description of module1
module2
    Description of module2

:author: Author Name
"""
```

## Tips for Effective Documentation

1. **Consistency**
    - Use consistent formatting throughout project
    - Maintain same level of detail for similar items
    - Use parallel structure in descriptions

2. **Clarity**
    - Be explicit about types
    - Document all exceptions
    - Include examples for non-obvious usage

3. **Maintenance**
    - Keep documentation synchronized with code
    - Update examples when interfaces change
    - Remove outdated information promptly

4. **Sphinx Integration**
    - Use proper field names for Sphinx compatibility
    - Include proper cross-references
    - Test documentation building regularly

---

# Google-Style Python Documentation Guide

## Overview
Google-style docstrings provide a clean, readable format for Python documentation. This guide covers everything you need to document Python code effectively using Google style.

## Basic Structure
```python
"""Summary line.

Detailed description (optional).

Args:
    param1: Description of param1.
    param2 (type): Description of param2.

Returns:
    Description of return value.

Raises:
    ExceptionType: Why this exception occurs.
"""
```

## Standard Sections

### For Functions
- `Args:` - List of parameters
- `Returns:` - Description of return value
- `Raises:` - List of exceptions that may be raised
- `Examples:` - Code examples (optional)
- `Notes:` - Additional notes (optional)

### For Classes
- `Attributes:` - List of class attributes
- `Examples:` - Code examples (optional)
- `Note:` - Additional notes (optional)

## Code Examples

### Class Documentation
```python
class Rectangle:
    """A class to represent a rectangle.

    Detailed description of the rectangle class and its purpose.

    Attributes:
        width (float): The width of the rectangle.
        height (float): The height of the rectangle.
        area (float): The calculated area of the rectangle.
    """
```

### Method Documentation
```python
def calculate_area(length: float, width: float) -> float:
    """Calculates the area of a rectangle.

    Args:
        length: The length of the rectangle.
        width: The width of the rectangle.

    Returns:
        The area of the rectangle.

    Raises:
        ValueError: If either length or width is negative.
    
    Examples:
        >>> calculate_area(2, 3)
        6.0
    """
```

### Property Documentation
```python
@property
def area(self) -> float:
    """The area of the rectangle.

    Returns:
        The calculated area using width * height.
    """
```

## Best Practices

### Do's
- Write a clear, one-line summary
- Leave a blank line after the summary if adding more details
- Indent subsections with 4 spaces
- Use consistent capitalization and punctuation
- Include types in Args section if not using type hints
- Document all public methods and classes
- Be specific about raised exceptions

### Don'ts
- Don't restate obvious information
- Don't describe implementation details (focus on behavior)
- Don't skip documenting exceptions
- Don't exceed 72-80 characters per line in docstrings
- Don't repeat information that's clear from the type hints

## Examples by Complexity

### Simple Function
```python
def add(x: int, y: int) -> int:
    """Adds two numbers.

    Args:
        x: First number.
        y: Second number.

    Returns:
        The sum of x and y.
    """
```

### Complex Function
```python
def process_data(data: list[dict], 
                threshold: float = 0.5, 
                normalize: bool = False) -> tuple[list, dict]:
    """Processes a list of data points according to specified parameters.

    Analyzes each data point and filters based on threshold value.
    Optionally normalizes the data before processing.

    Args:
        data: List of dictionaries containing data points.
            Each dict must have 'value' and 'timestamp' keys.
        threshold: Minimum value to include in results. Defaults to 0.5.
        normalize: Whether to normalize values before processing.
            Defaults to False.

    Returns:
        A tuple containing:
            - List of processed data points
            - Dictionary of processing statistics

    Raises:
        ValueError: If threshold is negative.
        KeyError: If any data point is missing required keys.
        TypeError: If data is not a list of dictionaries.

    Examples:
        >>> data = [{'value': 1.0, 'timestamp': '2024-01-01'}]
        >>> process_data(data, threshold=0.8)
        ([{'value': 1.0, 'timestamp': '2024-01-01'}], {'processed': 1})
    """
```

## Style Conventions

### Indentation
```python
"""Summary line.

    Detailed description is indented by 4 spaces.

    Args:
        param1: Description indented.
            Long descriptions can wrap with hanging indent.
        param2: Another parameter.
"""
```

### Line Length
- Aim for maximum 72-80 characters per line
- Use hanging indents for wrapped lines
- Keep examples concise but clear

### Formatting
- Use regular sentences with periods
- Capitalize first word of each section
- Be consistent with terminology
- Use parallel structure in descriptions

## Tips for Effective Documentation

1. **Focus on Behavior**
    - Document what the code does, not how it does it
    - Explain edge cases and special conditions
    - Highlight important assumptions

2. **Be Complete**
    - Document all parameters and return values
    - List all possible exceptions
    - Include examples for complex functionality

3. **Stay Current**
    - Update docs when code changes
    - Remove outdated examples
    - Keep lists of exceptions current

4. **Consider the Reader**
    - Write for your audience's expertise level
    - Include examples for complex cases
    - Explain rationale for non-obvious choices