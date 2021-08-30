.. currentmodule:: mutiny.errors

.. _api-errors:

Exceptions
==========

The following custom exceptions are thrown by the library.

.. jinja:: autodoc

    {% for cls in classes("mutiny.errors") %}
    {{ cls.__name__ }}
    {{ cls.__name__ | length * "-" }}

    .. autoclass:: {{ cls.__name__ }}
        :show-inheritance:
        :members:
    {% endfor %}
