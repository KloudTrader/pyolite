import re
from unipath import Path

from pyolite.repo import Repo
from pyolite.patterns import CONFIG_PATTERN
from pyolite.models.lists import ListUsers


class Repository(object):
    def __init__(self, name, path, git):
        self.name = name
        self.path = path
        self.git = git

        self.repo = Repo(Path(path,
                              "conf/repos/%s.conf" % name))

        self.users = ListUsers(self)

    @classmethod
    def get_by_name(cls, lookup_repo, path, git):
        for obj in Path(path, 'conf').walk():
            if obj.isdir():
                continue

            with open(str(obj)) as f:
                if "repo %s" % lookup_repo in f.read():
                    return cls(lookup_repo, path, git)
        return None

    @property
    def config(self):
        return self._serialize_config()

    @config.setter
    def config(self, values):
        if isinstance(values, dict):
            raw_values = values.items()
        elif isinstance(values, list) or isinstance(values, set) or isinstance(values, tuple):
            if len(values) > 2:
                raise ValueError("Use a dict if you want to set multiple values.")
            raw_values = [values]
        else:
            raise ValueError("Accepted config types are: dict, tuple, list and set.")

        current_config = self._read_current_config()
        for config in raw_values:
            current_config[config[0]] = config[1]

        self.repo.set_config(self._serialize_config(current_config))

    def _serialize_config(self, structured_config=None):
        structured_config = structured_config or self._read_current_config()

        config = ""
        for name, value in structured_config.iteritems():
            config += "    config %s    =    %s\n" % (name, value)
        return config

    def _read_current_config(self):
        return {
            result.group(2): result.group(5)
            for result in re.finditer(CONFIG_PATTERN, self.repo.read())
        }

    def __str__(self):
        return "< %s >" % self.name
