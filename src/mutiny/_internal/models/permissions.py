# Copyright 2021 Jakub Kuczys (https://github.com/jack1142)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import final

from .bases import BitField, bit

__all__ = ("UserPermissions", "ChannelPermissions", "ServerPermissions")


@final
class UserPermissions(BitField):
    access = bit(1)
    view_profile = bit(2)
    send_message = bit(4)
    invite = bit(8)


@final
class ChannelPermissions(BitField):
    view = bit(1)
    send_message = bit(2)
    manage_messages = bit(4)
    manage_channel = bit(8)
    voice_call = bit(16)
    invite_others = bit(32)
    embed_links = bit(64)
    upload_files = bit(128)


@final
class ServerPermissions(BitField):
    view = bit(1)
    manage_roles = bit(2)
    manage_channels = bit(4)
    manage_server = bit(8)
    kick_members = bit(16)
    ban_members = bit(32)
    change_nickname = bit(4096)
    manage_nicknames = bit(8192)
    change_avatar = bit(16382)
    remove_avatars = bit(32768)
