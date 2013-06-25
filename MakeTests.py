#!/usr/bin/env python
import jinja2
import os
import sys


class PuppetTest:
    """
    This class represents single test of the Puppet module.
    """

    def __init__(self, file_path):
        """
        You should give this constructor the full path to the tests' file.
        """
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.test_name = self.file_name.replace('.pp', '').title()

    def getPath(self):
        """
        Returns full path to the tests' file
        """
        return self.file_path

    def getFile(self):
        """
        Returns only name of this tests' file
        """
        return self.file_name

    def getName(self):
        """
        Returns title cased tests' name
        """
        return self.test_name

    def __repr__(self):
        """
        String representation of PuppetTest
        """
        return "PuppetTest: Name: %s Path: %s File: %s" % (self.getName(), self.getPath(), self.getFile())


class PuppetModule:
    """
    This class represents Puppet module
    """

    def __init__(self, module_path):
        """
        You should give this constructor the full path to the module
        """
        self.module_path = module_path
        self.module_name = os.path.basename(self.module_path)
        self.tests = []
        self.findTests()

    def findTests(self):
        """
        Find all tests in this module and fill tests array with PuppetTest objects.
        """
        tests_path = os.path.join(self.module_path, 'tests')
        for test_file in os.listdir(tests_path):
            if not test_file[-3:] == '.pp':
                continue
            full_test_path = os.path.join(self.module_path, 'tests', test_file)
            puppet_test = PuppetTest(full_test_path)
            self.tests.append(puppet_test)

    def getTests(self):
        """
        Return array of PuppetTest objects found in this module
        """
        return self.tests

    def getName(self):
        """
        Returns module's name
        """
        return self.module_name

    def getPath(self):
        """
        Returns full path to this module
        """
        return self.module_path

    def __repr__(self):
        """
        String representation of PuppetModule
        """
        tpl = "\nPuppetModule: Name: %s Path: %s\n" % (self.getName(), self.getPath())
        if len(self.tests) > 0:
            tpl += "  Tests:\n"
            tests = ["  " + repr(test) for test in self.tests]
            tpl += "\n".join(tests)
        return tpl


class MakeTests:
    """
    This is main class. It finds all modules in the given directory and creates tests for them.
    """

    def __init__(self, module_library_path, tests_directory_path):
        """
        You should give path to modules library and path to output tests directory to this constructor
        """
        if not os.path.isdir(module_library_path):
            print "No such dir " + module_library_path
            exit(1)

        self.template_loader = jinja2.FileSystemLoader(searchpath="templates")
        self.template_environment = templateEnv = jinja2.Environment(
            loader=self.template_loader,
        )
        self.module_path = "/etc/puppet/modules"
        self.manifests_path = "/etc/puppet/manifests"
        self.module_library_path = module_library_path
        self.tests_directory_path = tests_directory_path
        self.template_file = "puppet_module_test.py"
        self.modules = []
        self.findModules()

    def setTemplateFile(self, template_file):
        """
        Set script template file
        """
        self.template_file = template_file

    def setModulePath(self, module_path):
        """
        Set path to modules inside virtual machine
        """
        self.module_path = module_path

    def setManifestsPath(self, manifests_path):
        """
        Set path to manifests directory inside virtual machine
        """
        self.manifests_path = manifests_path

    def getModules(self):
        """
        Get array of PuppetModule objects
        """
        return self.modules

    def findModules(self):
        """
        Find all Puppet modules in module_library_path
        and create array of PuppetModule objects
        """
        for module_dir in os.listdir(self.module_library_path):
            tests_dir = os.path.join(self.module_library_path, module_dir, 'tests')
            if not os.path.isdir(tests_dir):
                continue
            full_module_dir = os.path.join(self.module_library_path, module_dir)
            puppet_module = PuppetModule(full_module_dir)
            self.modules.append(puppet_module)

    def compileScript(self, module):
        """
        Compile script template for given module and return it
        """
        template = self.template_environment.get_template(self.template_file)
        compiled_template = template.render(
            module_path=self.module_path,
            manifests_path=self.manifests_path,
            module_name=module.getName(),
            tests=module.getTests(),
        )
        return compiled_template

    def makeAllScripts(self):
        """
        Compile and save to tests_directory_path all the test scripts. Main procedure.
        """
        for module in self.getModules():
            print self.compileScript(module)

if __name__ == '__main__':
    MT = MakeTests(sys.argv[1])
    MT.makeAllScripts()
