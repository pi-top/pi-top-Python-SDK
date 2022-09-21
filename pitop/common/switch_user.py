import grp
import os
import pwd


def env_for_user(user, env=None):
    """Returns an environment variables dictionary, intended for use as the env
    parameter when spawining a process as another user.

    Takes the initial env as a param or from the current environment and
    modifies user-specific parts to suit the new user. Use-case specific
    variables such as DISPLAY should be set outside.
    """

    if get_uid(user) is None:
        raise Exception(f"User not found: {user}")

    if not isinstance(env, dict):
        env = os.environ.copy()

    env["USER"] = user
    env["LOGNAME"] = user
    env["HOME"] = get_home_directory(user)
    env["XDG_RUNTIME_DIR"] = get_xdg_runtime_dir(user)
    env["SHELL"] = get_shell(user)

    # remove None values
    env = {k: v for k, v in env.items() if v is not None}
    return env


def switch_user(user):
    """Primarily intended for use as the preexec_fn when spawning a process as
    another user.

    In combination with env_for_user this is equivalent to running the
    process with `su` or `sudo -u`.
    """

    if get_uid(user) is None:
        raise Exception(f"User not found: {user}")

    # set the process group id for user
    os.setgid(get_gid(user))

    # set the process supplemental groups for user
    os.setgroups(get_grp_ids(user))

    # set the process user id
    # must do this after setting groups as it reduces privilege
    os.setuid(get_uid(user))

    # create a new session and process group for the user process and
    # subprocesses. this allows us to clean them up in one go as well
    # as allowing a shell process to be a 'controlling terminal'
    os.setsid()


def get_uid(user):
    try:
        return pwd.getpwnam(user).pw_uid
    except (KeyError, TypeError):
        return None


def get_gid(user):
    try:
        return pwd.getpwnam(user).pw_gid
    except (KeyError, TypeError):
        return None


def get_grp_ids(user):
    try:
        groups = [g.gr_gid for g in grp.getgrall() if user in g.gr_mem]
        gid = pwd.getpwnam(user).pw_gid
        groups.append(gid)
        return groups
    except (KeyError, TypeError):
        return None


def get_shell(user):
    try:
        return pwd.getpwnam(user).pw_shell
    except (KeyError, TypeError):
        return None


def get_home_directory(user):
    try:
        return pwd.getpwnam(user).pw_dir
    except (KeyError, TypeError):
        return None


def get_xdg_runtime_dir(user=None):
    uid = get_uid(user)
    xdg_runtime_dir = f"/run/user/{uid}"

    if os.path.exists(xdg_runtime_dir):
        return xdg_runtime_dir

    return None
