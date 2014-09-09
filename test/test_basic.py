import perm
import pytest

import example


def test_unique():
    assert str(example.Project.write) != str(example.Project.read)


def test_constant():
    old = str(example.Project.write)
    new = str(reload(example).Project.write)
    assert old == new


def test_basic():
    user = perm.User()
    assert not user.has_perm(example.Project.read, 1)
    user.add_perm(example.Project.read, 1)
    assert user.has_perm(example.Project.read, 1)

    assert not user.has_perm(example.Project.read, 2)
    # add permission to read all projects
    user.add_perm(example.Project.read)
    assert user.has_perm(example.Project.read, 2)


def test_require():
    user = perm.User()
    with pytest.raises(perm.PermissionDenied):
        user.require_perm(example.Project.read)

    class CustomPermissionDenied(Exception):
        def __init__(self, permission, subject):
            super(CustomPermissionDenied, self).__init__('Message')

    perm.PERMISSION_DENIED_EXCEPTION = CustomPermissionDenied

    with pytest.raises(CustomPermissionDenied):
        user.require_perm(example.Project.read)


def test_double_perms():
    """inserting a permission twice should not have any effect"""
    user = perm.User()
    assert len(user.get('perm', [])) == 0

    user.add_perm(example.Project.read, 1)
    assert len(user.get('perm', [])) == 1

    user.add_perm(example.Project.read, 1)
    assert len(user.get('perm', [])) == 1

    user.add_perm(example.Project.read, 123)
    assert len(user.get('perm', [])) == 2


def test_add_role():
    user = perm.User()

    # variable 'project' must be defined
    with pytest.raises(perm.MissingVariable):
        user.add_role(example.ProjectAdmin)

    user.add_role(example.ProjectAdmin, project=1)


def test_role_permissions():
    """The project admin role grants write access to specific projects"""
    user = perm.User()
    assert not user.has_perm(example.Project.write, 1)

    user.add_role(example.Useless)
    assert not user.has_perm(example.Project.write, 1)

    user.add_role(example.ProjectAdmin, project=1)
    assert user.has_perm(example.Project.write, 1)
    assert not user.has_perm(example.Project.write, 2)


def test_role_general_grant():
    """The project admin role grants read access to ALL projects"""
    user = perm.User()
    assert not user.has_perm(example.Project.read, 1)
    assert not user.has_perm(example.Project.read, 2)

    user.add_role(example.ProjectAdmin, project=1)
    print user
    assert user.has_perm(example.Project.read, 1)
    assert user.has_perm(example.Project.read, 2)

## WIP
# def test_group():
#     user = perm.User()
#
#     group = perm.Group()