"""
Utility functions used by tests
"""

import uuid

from volue.mesh import AttributeBase, Object

CHIMNEY_1_ID = uuid.UUID("0000000A-0004-0000-0000-000000000000")
CHIMNEY_2_ID = uuid.UUID("0000000A-0005-0000-0000-000000000000")

# Dummy unit of measurement 'unit' values used for testing.
UNIT_1 = "m"
UNIT_2 = "cm"


class AttributeForTesting(AttributeBase):
    """
    Redefinition of AttributeBase class, we are NOT calling super().__init__(),
    but only define ID and path fields needed for unit tests.

    AttributeBase itself requires proto attribute to be initialized.
    """

    def __init__(self):
        self.id = uuid.uuid4()
        self.path = "test_attribute_path"


class ObjectForTesting(Object):
    """
    Redefinition of Object class, we are NOT calling super().__init__(),
    but only define ID and path fields needed for unit tests.

    Object itself requires to define complete list of fields, whereas we
    need only 2 of them in unit tests.
    """

    def __init__(self):
        self.id = uuid.uuid4()
        self.path = "test_object_path"


class AttributeDefinitionForTesting(AttributeBase.AttributeBaseDefinition):
    """
    Redefinition of AttributeBase.AttributeBaseDefinition class, we are NOT
    calling super().__init__(), but only define ID and path fields needed
    for unit tests.

    AttributeBase.AttributeBaseDefinition itself requires proto attribute
    definition to be initialized.
    """

    def __init__(self):
        self.id = uuid.uuid4()
        self.path = "test_attribute_definition_path"
