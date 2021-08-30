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

__all__ = (
    "MutinyException",
    "AuthenticationError",
    "InvalidCredentials",
    "OnboardingNotFinished",
)


class MutinyException(Exception):
    """A base class for all of the Mutiny's exceptions."""


class AuthenticationError(MutinyException):
    """A base class for the authentication errors."""


class InvalidCredentials(AuthenticationError):
    """Thrown when the authentication has failed due to incorrect credentials."""


class OnboardingNotFinished(AuthenticationError):
    """
    Thrown when trying to authenticate as a user that has not done onboarding
    (choosing a username after account registration) yet.
    """
