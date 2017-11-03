import method
import yaml

# XXX If this class ends up growing, it would make sense to put it in its own
# file somewhere.
class Version(object):
    def __init__(self, config):
        self.name = config['name']
        self.targets = config.get('targets')
        if 'giturl' in config:
            self.giturl = config['giturl']
            self.branch = config.get('branch', self.name)


def get_versions():
    config = {}
    with open('versions.yaml') as version_file:
        config = yaml.load(version_file)

    origins = [Version(version_cfg) for version_cfg in config['versions']]
    targets = {key, Version(version_cfg) for key,version_cfg in
               config['targets'].iteritems()}
    return origins, targets


def get_tests():
    with open('tests/tests.yaml') as test_file:
        config = yaml.load(test_file)

    tests = config['tests']


def run_tests():
    origins, targets = get_versions()
    tests = get_tests()

    for test in tests:
        for origin in orgins:
            run_test(test, origin)


# XXX Currently no command line arguments can be given. Useful ones to include
# would be:
# * a flag to specify a single test to run (by name)
# * a flag to list all tests and return
# * a flag to list help text
if __name__ == "main":
    run_tests()
