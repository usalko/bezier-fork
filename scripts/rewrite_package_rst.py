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

"""Replace autogenerated contents of bezier package RST.

This is needed since the presence of ``__all__`` in
the package ``__init__.py`` causes Sphinx to try to document
each included element multiple times.
"""

import os
import types

try:
    import bezier
except ImportError:
    bezier = None


SPECIAL_MEMBERS = ("__author__", "__version__")
UNDOCUMENTED_SPECIAL_MEMBERS = ("__author__",)
EXPECTED = """\
bezier package
==============

.. automodule:: bezier
   :members:
   :inherited-members:
   :undoc-members:
   :show-inheritance:

Subpackages
-----------

.. toctree::
   :maxdepth: 4

   bezier.hazmat

Submodules
----------

.. toctree::
   :maxdepth: 4

   bezier.curve
   bezier.curved_polygon
   bezier.triangle
"""
DESIRED_TEMPLATE = """\
bezier package
==============

.. automodule:: bezier{members}

Submodules
----------

.. toctree::

   bezier.curve
   bezier.curved_polygon
   bezier.triangle

Subpackages
-----------

.. toctree::

   bezier.hazmat
"""
_SCRIPTS_DIR = os.path.dirname(__file__)
_DOCS_DIR = os.path.abspath(os.path.join(_SCRIPTS_DIR, os.pardir, "docs"))
FILENAME = os.path.join(_DOCS_DIR, "python", "reference", "bezier.rst")


def get_public_members():
    """Get public members in :mod:`bezier` package.

    Also validates the contents of ``bezier.__all__``.

    Returns:
        list: List of all public members **defined** in the
        main package (i.e. in ``__init__.py``).

    Raises:
        ValueError: If ``__all__`` has repeated elements.
        ValueError: If the "public" members in ``__init__.py`` don't match
            the members described in ``__all__``.
    """
    if bezier is None:
        return []

    local_members = []
    all_members = set()
    for name in dir(bezier):
        # Filter out non-public.
        if name.startswith("_") and name not in SPECIAL_MEMBERS:
            continue

        value = getattr(bezier, name)
        # Filter out imported modules.
        if isinstance(value, types.ModuleType):
            continue

        all_members.add(name)
        # Only keep values defined in the base package.
        home = getattr(value, "__module__", "bezier")
        if home == "bezier":
            local_members.append(name)
    size_all = len(bezier.__all__)
    all_exports = set(bezier.__all__)
    if len(all_exports) != size_all:
        raise ValueError("__all__ has repeated elements")

    if all_exports != all_members:
        raise ValueError(
            "__all__ does not agree with the publicly imported members",
            all_exports,
            all_members,
        )

    local_members = [
        member
        for member in local_members
        if member not in UNDOCUMENTED_SPECIAL_MEMBERS
    ]
    return local_members


def get_desired():
    """Populate ``DESIRED_TEMPLATE`` with public members.

    If there are no members, does nothing.

    Returns:
        str: The "desired" contents of ``bezier.rst``.
    """
    public_members = get_public_members()
    if public_members:
        members = "\n    :members: {}".format(", ".join(public_members))
    else:
        members = ""
    return DESIRED_TEMPLATE.format(members=members)


def main():
    """Main entry point to replace autogenerated contents.

    Raises:
        ValueError: If the file doesn't contain the expected or
            desired contents.
    """
    with open(FILENAME, "r") as file_obj:
        contents = file_obj.read()
    desired = get_desired()
    if contents == EXPECTED:
        with open(FILENAME, "w") as file_obj:
            file_obj.write(desired)
    elif contents != desired:
        raise ValueError("Unexpected contents", contents, "Expected", EXPECTED)


if __name__ == "__main__":
    main()
