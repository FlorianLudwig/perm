import perm

Project = perm.Subject(__name__, 'project')
Project.read = perm.Permission()
Project.write = perm.Permission()


# a project admin might read and write the project
# he is admin of and read every project
ProjectAdmin = perm.Role(__name__, 'project_admin')
ProjectAdmin.add_variable('project', Project.read, Project.write)
ProjectAdmin.grant(Project.read)


Useless = perm.Role()