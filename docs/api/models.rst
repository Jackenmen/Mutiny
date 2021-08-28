.. currentmodule:: mutiny.models

.. _api-models:

Models
======

Models are classes that are received from Revolt API
and are not meant to be created by the user of the library.

.. danger::

    The classes listed below are **not intended to be created by users** and are also
    **read-only**.

    For example, this means that you should not make your own `mutiny.models.User`
    instances nor should you modify the `mutiny.models.User` instance yourself.

    If you want to get one of these model classes instances, you should do that by using
    appropriate methods and attributes on the `mutiny.Client`, `events`, and `models`.

.. jinja:: autodoc

    {% for module, classes in grouped_classes("mutiny.models") %}

    {{ module.__doc__ }}
    {{ module.__doc__ | length * "-" }}

    {% for cls in classes %}

    {{ cls.__name__ }}
    {{ cls.__name__ | length * "~" }}

    .. autoclass:: {{ cls.__name__ }}
        :members:
        :inherited-members:

    {% endfor %}

    {% endfor %}
