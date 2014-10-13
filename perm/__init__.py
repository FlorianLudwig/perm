KNOWN_ROLES = {}


class PermissionDenied(Exception):
    def __init__(self, permission, subject):
        msg = 'Permission {} for {} not granted'.format(permission, subject)
        super(PermissionDenied, self).__init__(msg)


class MissingVariable(Exception):
    pass


class Subject(object):
    def __init__(self, *name):
        object.__setattr__(self, '_name', '.'.join(name))

    def __str__(self):
        return self._name

    def __setattr__(self, key, value):
        """
        :param str key:
        :param Permission value:
        :return:
        """
        if not isinstance(value, Permission):
            raise AttributeError("Attributes of subject must be perm.Permission")
        value.name = key
        value.subject = self
        super(Subject, self).__setattr__(key, value)


class Permission(object):
    def __init__(self):
        self.name = None
        self.subject = None

    def __str__(self):
        assert self.name, 'Name must be set before use'
        return '{}.{}'.format(str(self.subject), self.name)


class Role(object):
    def __init__(self, *name):
        self.variables = {}
        self.permissions = set()
        self.name = '.'.join(name)
        KNOWN_ROLES[self.name] = self

    def __str__(self):
        return self.name

    def has_perm(self, permission, subject=None, variable_values=None):
        if permission in self.permissions:
            return True
        if variable_values:
            for name, var in self.variables.items():
                if permission in var:
                    test_sub = variable_values[name]
                    if match_subject(subject, test_sub):
                        return True
        return False

    def add_variable(self, var_name, *permissions):
        if var_name in self.variables:
            raise AttributeError('Variable {} already exists'.format(var_name))
        self.variables[var_name] = permissions

    def grant(self, *permissions):
        self.permissions.update(permissions)


def match_subject(subject, check):
    """Check if `check` does match the `subject`

    :param dict|object subject:
    :param dict|object check:
    :return bool:
    """
    if check is None:
        return True
    if isinstance(subject, dict) and isinstance(check, dict):
        for key, value in check.items():
            if key not in subject or subject[key] != value:
                return False
        return True
    else:
        return subject == check


class UserBase(object):
    def has_perm(self, permission, subject=None):
        """Check if user got permission on subject

        :param permission:
        :type permission: perm.Permission
        :param subject: optional,
        :return:
        :rtype: bool
        """
        for test_perm, test_sub in self.get('perm', []):
            if test_perm == permission.name and match_subject(subject, test_sub):
                return True

        for role, variables in self.get('roles', []):
            if KNOWN_ROLES[role].has_perm(permission, subject, variables):
                return True

        return False

    def require_perm(self, permission, subject=None):
        """check if user got permission on subject otherwise raise

        To customize what exception is raised set
        perm.PERMISSION_DENIED_EXCEPTION

        :param Permission permission:
        :param subject: optional,
        :return:
        :rtype: None
        """
        if not self.has_perm(permission, subject):
            raise PERMISSION_DENIED_EXCEPTION(permission, subject)

    def require_login(self):
        return True

    def add_perm(self, permission, subject=None):
        """add permission to user

        :param Permission permission:
        :param subject: optional,
        :return:
        :rtype: None
        """
        store = self.setdefault('perm', [])
        perm = (permission.name, subject)
        if perm not in store:
            store.append(perm)

    def add_role(self, role, **variables):
        """Add a new role to user

        :param Role role: Role to remove
        :param variables: Role variables
        """
        roles = self.setdefault('roles', [])
        # check if all needed variabes are passed
        for key in role.variables:
            if key not in variables:
                raise MissingVariable(key)

        # use list instead of tuple so it can be json load/dump'ed
        user_role = [str(role), variables]
        if user_role not in roles:
            roles.append(user_role)

    def remove_role(self, role, **variables):
        """Remove a role from a user

        :param Role role: Role to remove
        :param variables: Role variables
        """
        roles = self.setdefault('roles', [])
        user_role = [str(role), variables]
        if user_role in roles:
            roles.remove(user_role)

    def has_role(self, role, **variables):
        """check if the user has the given role

        :param Role role: Role to check
        :param variables: Role variables
        """
        roles = self.get('roles', [])
        user_role = [str(role), variables]
        return user_role in roles


class AnonymousBase(UserBase):
    def require_login(self):
        raise PERMISSION_DENIED_EXCEPTION('user_login', None)


class User(UserBase, dict):
    pass


class Anonymous(AnonymousBase, dict):
    pass


PERMISSION_DENIED_EXCEPTION = PermissionDenied
