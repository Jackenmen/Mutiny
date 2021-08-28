.. currentmodule:: mutiny.bits

.. _api-bits:

Bit fields
==========

Some of the fields in the API models are represented by bit fields.
These wrappers allow for easy access and write to the individual bits as well as
some other common operations like equality comparisons.

.. jinja:: autodoc

    {% for cls in classes("mutiny.bits") %}
    {{ cls.__name__ }}
    {{ cls.__name__ | length * "-" }}

    .. autoclass:: {{ cls.__name__ }}
        :members:
        :inherited-members:
        :special-members: __eq__, __ne__
    {% endfor %}
