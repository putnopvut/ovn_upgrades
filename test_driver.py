#!/usr/bin/env python

import yaml
import os
import subprocess


# XXX If this class ends up growing, it would make sense to put it in its own
# file somewhere.
class Version(object):
    def __init__(self, config):
        self.name = config.get('name')
        self.targets = config.get('targets')
        if 'giturl' in config:
            self.giturl = config['giturl']
            self.branch = config.get('branch', self.name)


def get_versions():
    config = {}
    with open('versions.yaml') as version_file:
        config = yaml.load(version_file)

    origins = [Version(version_cfg) for version_cfg in config['versions']]
    targets = {version_cfg['name']: Version(version_cfg) for version_cfg
               in config['targets']}
    return origins, targets


def get_tests():
    with open('tests/tests.yaml') as test_file:
        config = yaml.load(test_file)

    tests = config['tests']
    return tests


def run_test(test, origin, targets):

    for target_name in origin.targets:
        # XXX Each iteration of this loop could be run in parallel. There is no
        # good reason for each test run to run in series.
        if target_name not in targets:
            print "Error: Unknown target version {0}".format(target_name)

        target = targets[target_name]
        print "Testing upgrade from version {0} to {1}".format(origin.name,
                                                               target_name)

        # XXX this is currently not fault tolerant at all.
        # * If the script file does not exist, then this will throw an
        #   exception.
        # * There is no checking to be sure that the scripts do not error
        #   out.
        # * The shutdown script should be called even if any of the previous
        #   scripts fail.
        test_dir = os.path.join(os.getcwd(), 'tests', test)
        setup_script = os.path.join(test_dir, 'setup')

        subprocess.Popen([setup_script, origin.name, origin.giturl,
                          origin.branch]).communicate()

        pre_upgrade_script = os.path.join(test_dir, 'pre-upgrade')
        subprocess.Popen([pre_upgrade_script]).communicate()

        upgrade_script = os.path.join(test_dir, 'upgrade')
        subprocess.Popen([upgrade_script, target.giturl,
                          target.branch]).communicate()

        post_upgrade_script = os.path.join(test_dir, 'post-upgrade')
        subprocess.Popen([post_upgrade_script]).communicate()

        shutdown_script = os.path.join(test_dir, 'shutdown')
        subprocess.Popen([shutdown_script]).communicate()


def run_tests():
    origins, targets = get_versions()
    tests = get_tests()

    for test in tests:
        for origin in origins:
            run_test(test, origin, targets)


# XXX Currently no command line arguments can be given. Useful ones to include
# would be:
# * a flag to specify a single test to run (by name)
# * a flag to list all tests and return
# * a flag to list help text
if __name__ == "__main__":
    run_tests()
