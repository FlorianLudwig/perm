import perm

Project = perm.Subject(__name__, 'project')
Project.read = perm.Permission()
Project.write = perm.Permission()
