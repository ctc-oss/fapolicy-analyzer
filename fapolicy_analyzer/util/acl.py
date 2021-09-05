import grp
import subprocess


def getUserDetails(uid):
    result = subprocess.getstatusoutput(f"id '{uid}'")
    return result[1] if result[0] == 0 else ""


def getGroupDetails(gid):
    result = grp.getgrgid(gid)
    return f"name={result[0]} gid={result[2]} users={','.join(result[3])}"
