import perm


class Project(perm.Subject):
    read = perm.Permission()
    write = perm.Permission()


class ProjectAdmin(perm.Role):
    project = perm.Variable()
    project.grant(
        Project.read, Project.write
    )

    perm.grant(
        Project.read
    )

