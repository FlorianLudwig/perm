import imp
import json

import pytest

import perm

import example
import example2


def test_naming():
    # names must be unique
    assert str(example.Project.write) != str(example.Project.read)
    assert str(example.Project.write) != str(example2.Project.write)


def test_constant():
    old = str(example.Project.write)
    new = str(imp.reload(example).Project.write)
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
    assert user.has_perm(example.Project.read, 1)
    assert user.has_perm(example.Project.read, 2)


def test_jsonablity():
    user = perm.User()
    user.add_perm(example.Project.read, 1)

    j = json.dumps(user)
    data = json.loads(j)
    user = perm.User(data)
    assert user.has_perm(example.Project.read, 1)


def test_dict_subjects():
    user = perm.User()
    p1 = {'_id': 1, 'group': 0}
    p2 = {'_id': 2, 'group': 0}
    assert not user.has_perm(example.Project.read, p1)
    assert not user.has_perm(example.Project.read, p2)

    user.add_perm(example.Project.read, {'_id': 1})
    assert user.has_perm(example.Project.read, p1)
    assert not user.has_perm(example.Project.read, p2)

    user = perm.User()
    user.add_perm(example.Project.read, {'group': 0})
    assert user.has_perm(example.Project.read, p1)
    assert user.has_perm(example.Project.read, p2)

    user = perm.User()
    user.add_role(example.ProjectAdmin, project={'group': 0})
    assert user.has_perm(example.Project.write, p1)
    assert user.has_perm(example.Project.write, p2)
