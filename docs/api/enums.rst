.. currentmodule:: mutiny.enums

.. _api-enums:

Enums
=====

The API provides some enumerations for certain types of strings to avoid the API
from being stringly typed in case the strings change in the future.

.. jinja:: autodoc

    {% for cls in classes("mutiny.enums") %}
    {{ cls.__name__ }}
    {{ cls.__name__ | length * "-" }}

    .. autoclass:: {{ cls.__name__ }}
        :members:
        :inherited-members:
    {% endfor %}
