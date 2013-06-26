#!/usr/bin/env python
import jinja2
import os
import sys
from Interface import Interface


class PuppetTest:
    """
    This class represents single test of the Puppet module.
    """

    def __init__(self, test_file_path, interface):
        """
        You should give this constructor path to test file
        """
        self.__test_file_path = test_file_path
        self.__tests_path = os.path.dirname(self.__test_file_path)
        self.__test_file_name = os.path.basename(self.__test_file_path)
        self.__test_name = self.__test_file_name.replace('.pp', '')

    def getPath(self):
        """
        Returns path to directory of this test
        """
        return self.__tests_path

    def getFile(self):
        """
        Returns file name of this test
        """
        return self.__test_file_name

    def getName(self):
        """
        Returns name of this test
        """
        return self.__test_name

    @property
    def path(self):
        return self.getPath()

    @property
    def file(self):
        return self.getFile()

    @property
    def name(self):
        return self.getName()

    def __repr__(self):
        """
        String representation of PuppetTest
        """
        return "PuppetTest(name=%s, path=%s, file=%s)" % (self.getName(), self.getPath(), self.getFile())


class PuppetModule:
    """
    This class represents Puppet module
    """

    def __init__(self, local_module_path, interface):
        """
        You should give this constructor the full path to the module
        """
        self.__local_module_path = local_module_path
        self.interface = interface
        self.__module_name = os.path.basename(self.__local_module_path)

        self.__tests = []

        self.findTests()

    def findTests(self):
        """
        Find all tests in this module and fill tests array with PuppetTest objects.
        """
        current_path = os.path.abspath(os.curdir)
        try:
            # try to change directory to test's folder
            os.chdir(self.__local_module_path)
        except OSError as error:
            self.interface.error("Cannot change directory to %s: %s" % (self.__local_module_path, error.message))
        else:
            # if change was successful start looking for tests
            for root, dirs, files in os.walk('tests'):
                for test_file in files:
                    if not test_file[-3:] == '.pp':
                        continue
                    test_file_path = os.path.join(root, test_file)
                    puppet_test = PuppetTest(test_file_path, self.interface)
                    self.__tests.append(puppet_test)
        finally:
            # try to restore original folder on exit
            try:
                os.chdir(current_path)
            except OSError as error:
                self.interface.error("Cannot change directory to %s: %s" % (self.__local_module_path, error.message), 1)

    def getTests(self):
        """
        Return array of PuppetTest objects found in this module
        """
        return self.__tests

    def getName(self):
        """
        Returns module's name
        """
        return self.__module_name

    def getPath(self):
        """
        Returns full path to this module
        """
        return self.__local_module_path

    @property
    def tests(self):
        return self.getTests()

    @property
    def name(self):
        return self.getName()

    @property
    def path(self):
        return self.getPath()

    def __repr__(self):
        """
        String representation of PuppetModule
        """
        tests_string = ''
        if len(self.tests) > 0:
            tests = [repr(test) for test in self.tests]
            tests_string += ", ".join(tests)
        tpl = "PuppetModule(name=%s, path=%s, tests=[%s]" % (self.getName(), self.getPath(), tests_string)

        return tpl


class MakeTests:
    """
    This is main class. It finds all modules in the given directory and creates tests for them.
    """

    def __init__(self, tests_directory_path, local_modules_path, modules_path=None):
        """
        You should give to this constructor following arguments:
        module_library_path = Path to puppet modules which will be scanned for test files
        tests_directory_path = Output directory where files will be written
        modules_internal_path = (Optional) Use this path to modules in template instead of module_library_path.
        Useful when path to puppet modules differ on machine where tests are made and where they are executed.
        """
        self.interface = Interface(debuglevel=4)
        self.interface.debug('Starting MakeTests', 1)

        if not os.path.isdir(local_modules_path):
            self.interface.error('No such dir: ' + local_modules_path, 1)

        if not os.path.isdir(tests_directory_path):
            self.interface.error('No such dir: ' + tests_directory_path, 1)

        self.__local_modules_path = local_modules_path
        self.__modules_path = local_modules_path
        if modules_path:
            self.__modules_path = modules_path
        self.__tests_directory_path = tests_directory_path

        self.__default_template_file = 'puppet_module_test.py'
        self.__test_file_name_prefix = 'TestPuppetModule'

        self.__modules = []
        self.__module_templates = {}
        self.__make_tests_dir = os.path.dirname(os.path.abspath(__file__))

        self.setTemplatesDir('templates')
        self.setInternalModulesPath('/etc/puppet/modules')
        self.setInternalManifestsPath('/etc/puppet/manifests')

        self.findModules()

    def setTemplatesDir(self, template_dir):
        """
        Set directory to take templates from
        """
        if not os.path.isdir(template_dir):
            self.interface.error("No such dir: " + template_dir)
        self.__template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        self.__template_environment = templateEnv = jinja2.Environment(
            loader=self.__template_loader,
        )

    def setModuleTemplates(self, module_templates_dictionary):
        """
        Set module template file override dictionary
        """
        if type(module_templates_dictionary) is dict:
            self.__module_templates = module_templates_dictionary
        else:
            self.interface.error("Argument is not Dictionary")

    def setDefaultTemplateFile(self, template_file):
        """
        Set default script template file
        """
        self.__default_template_file = template_file

    def setInternalModulesPath(self, internal_modules_path):
        """
        Set path to modules inside virtual machine
        """
        self.__internal_modules_path = internal_modules_path

    def setInternalManifestsPath(self, internal_manifests_path):
        """
        Set path to manifests directory inside virtual machine
        """
        self.__internal_manifests_path = internal_manifests_path

    def getModulesList(self):
        """
        Get list of PuppetModule objects
        """
        return self.__modules

    def findModules(self):
        """
        Find all Puppet modules in module_library_path
        and create array of PuppetModule objects
        """
        self.interface.debug('Starting findModules in "%s"' % self.__local_modules_path, 2)
        for module_dir in os.listdir(self.__local_modules_path):
            full_local_module_path = os.path.join(self.__local_modules_path, module_dir)
            full_local_tests_path = os.path.join(full_local_module_path, 'tests')
            if not os.path.isdir(full_local_tests_path):
                continue
            self.interface.debug('Found Puppet module: "%s"' % full_local_module_path, 3)
            puppet_module = PuppetModule(full_local_module_path, self.interface)
            self.__modules.append(puppet_module)

    def compileScript(self, module):
        """
        Compile script template for given module and return it
        """
        template_file = self.__module_templates.get(module.getName(), self.__default_template_file)
        template = self.__template_environment.get_template(template_file)
        general = {
            'modules_path': self.__modules_path,
            'local_modules_path': self.__local_modules_path,
            'internal_modules_path': self.__internal_modules_path,
            'internal_manifests_path': self.__internal_manifests_path,
            'tests_directory_path': self.__tests_directory_path,
        }
        compiled_template = template.render(module=module, **general)
        return compiled_template

    def saveScript(self, module):
        """
        Saves compiled script to a file
        """
        file_name = self.__test_file_name_prefix + module.getName().title() + '.py'
        full_file_path = os.path.join(self.__tests_directory_path, file_name)
        script_content = self.compileScript(module)
        script_file = open(full_file_path, 'w+')
        script_file.write(script_content + "\n")
        script_file.close()

    def makeAllScripts(self):
        """
        Compile and save to tests_directory_path all the test scripts. Main procedure.
        """
        self.interface.debug('Starting makeAllScripts', 2)
        try:
            os.chdir(self.__make_tests_dir)
        except OSError as error:
            self.interface.error("Cannot change directory to %s: %s" % (self.__make_tests_dir, error.message))
            return None
        for module in self.getModulesList():
            self.interface.debug('Processing module: "%s"' % module.getName(), 3)
            self.saveScript(module)

    def removeAllTests(self):
        """
        Remove all tests from tests_directory_path
        """
        self.interface.debug('Starting removeAllTests in "%s"' % self.__tests_directory_path, 2)
        file_list = os.listdir(self.__tests_directory_path)
        for test_file in file_list:
            if not test_file[-3:] == '.py':
                continue
            if not test_file[0:16] == 'TestPuppetModule':
                continue
            full_file_path = os.path.join(self.__tests_directory_path, test_file)
            self.interface.debug('Removing test file: "%s"' % full_file_path, 3)
            os.remove(full_file_path)


if __name__ == '__main__':
    if len(sys.argv) > 3:
        MT = MakeTests(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        MT = MakeTests(sys.argv[1], sys.argv[2])

    MT.setModuleTemplates({'motd': 'motd_module_custom_test.py'})
    MT.removeAllTests()
    MT.makeAllScripts()
