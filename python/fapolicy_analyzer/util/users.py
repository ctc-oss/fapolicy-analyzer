import grp
import pwd
import subprocess


def getAllUsers():
    return sorted([u[0] for u in pwd.getpwall()])


def getAllGroups():
    return sorted([g[0] for g in grp.getgrall() if g[3]])


def getUserDetails(username):
    result = subprocess.getstatusoutput(f"id '{username}'")
    return result[1] if result[0] == 0 else ""


def getGroupDetails(groupname):
    result = grp.getgrnam(groupname)
    return f"name={result[0]} gid={result[2]} users={','.join(result[3])}"
