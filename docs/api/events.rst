.. currentmodule:: mutiny.events

.. _api-events:

Events
======

This page outlines the events that can be listened to by the `mutiny.Client`.

To register a function (event listener) that listens to an event, you can use the
`@Client.listen() <Client.listen()>` decorator or the `Client.add_listener()` method.

.. jinja:: autodoc

    {% for cls in classes("mutiny.events") %}
    {{ cls.__name__ }}
    {{ cls.__name__ | length * "-" }}

    .. autoclass:: {{ cls.__name__ }}
        :members:
        :inherited-members:
    {% endfor %}
