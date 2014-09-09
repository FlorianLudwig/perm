class PermissionDenied(Exception):
    def __init__(self, permission, subject):
        msg = 'Permission {} for {} not granted'.format(permission, subject)
        super(PermissionDenied, self).__init__(msg)


class MissingVariable(Exception):
    pass


class Subject(object):
    def __setattr__(self, key, value):
        """
        :param str key:
        :param Permission value:
        :return:
        """
        if not isinstance(value, Permission):
            raise AttributeError("Attributes of subject must be perm.Permission")
        value.name = key
        super(Subject, self).__setattr__(key, value)


class Permission(object):
    def __init__(self):
        self.name = None

    def __str__(self):
        assert self.name, 'Name must be set before use'
        return '{}.{}.{}'.format(self.__module__, self.__class__.__name__, self.name)


class Role(object):
    def __init__(self):
        self.variables = {}
        self.permissions = set()

    def has_perm(self, permission, subject=None, variable_values=None):
        if permission in self.permissions:
            return True
        if variable_values:
            for name, var in self.variables.items():
                if permission in var:
                    test_sub = variable_values[name]
                    if test_sub is None or subject == test_sub:
                        return True
        return False

    def add_variable(self, var_name, *permissions):
        if var_name in self.variables:
            raise AttributeError('Variable {} already exists'.format(var_name))
        self.variables[var_name] = permissions

    def grant(self, *permissions):
        self.permissions.update(permissions)


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
            if test_perm == permission and (test_sub == subject or test_sub is None):
                return True

        for role, variables in self.get('roles', []):
            if role.has_perm(permission, subject, variables):
                return True

        return False

    def require_perm(self, permission, subject=None):
        """check if user got permission on subject otherwise raise

        To customize what exception is raised set
        perm.PERMISSION_DENIED_EXCEPTION

        :param permission:
        :type permission: perm.Permission
        :param subject: optional,
        :return:
        :rtype: None
        """
        if not self.has_perm(permission, subject):
            raise PERMISSION_DENIED_EXCEPTION(permission, subject)

    def add_perm(self, permission, subject=None):
        """add permission to user

        :param permission:
        :type permission: perm.Permission
        :param subject: optional,
        :return:
        :rtype: None
        """
        perm = self.setdefault('perm', [])
        if not [permission, subject] in perm:
            perm.append([permission, subject])

    def add_role(self, role, **variables):
        """Add a new role to user

        :param Role role:
        :param variables:
        """
        roles = self.setdefault('roles', [])
        # check if all needed variabes are passed
        for key in role.variables:
            if key not in variables:
                raise MissingVariable(key)
        if not [role, variables] in roles:
            roles.append([role, variables])


class User(UserBase, dict):
    pass


PERMISSION_DENIED_EXCEPTION = PermissionDenied