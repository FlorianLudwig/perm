class PermissionDenied(Exception):
    def __init__(self, permission, subject):
        super(PermissionDenied, self).__init__('Permission {} for {} not granted'.format(permission, subject))


class MissingVariable(Exception):
    pass


class Permission(object):
    def __init__(self):
        self.name = None

    def __str__(self):
        assert self.name, 'Name must be set before use'
        return '{}.{}.{}'.format(self.__module__, self.__class__.__name__, self.name)


class Variable(object):
    def grant(self, *permissions):
        pass


class RoleMeta(type):
    def __new__(cls, name, bases, dct):
        dct['__variables'] = {}
        # collect names for permissions
        for key, value in dct.iteritems():
            if isinstance(value, Variable):
                dct['__variables'][key] = value
        return type.__new__(cls, name, bases, dct)


class Role(object):
    __metaclass__ = RoleMeta


class SubjectMeta(type):
    def __new__(cls, name, bases, dct):
        # collect names for permissions
        for key, value in dct.iteritems():
            if isinstance(value, Permission):
                value.name = key
        return type.__new__(cls, name, bases, dct)


class Subject(object):
    __metaclass__ = SubjectMeta




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
        return False

    def require_perm(self, permission, subject=None):
        """check if user got permussion on subject otherwise raise

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
        self.setdefault('perm', [])
        if not [permission, subject] in self['perm']:
            self['perm'].append([permission, subject])

    def add_role(self, role, **variables):
        self.setdefault('roles', [])
        # check if all needed variabes are passed
        for key in role.__variables:
            if key not in variables:
                raise MissingVariable(key)
        if not [role, variables] in self['perm']:
            self['perm'].append([role, variables])


class User(UserBase, dict):
    pass


def grant(*permissions):
    pass


PERMISSION_DENIED_EXCEPTION = PermissionDenied