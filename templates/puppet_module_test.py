import logging
from time import sleep
import unittest
from env_manager import EnvManager

LOG = logging.getLogger(__name__)

class TestPuppetModule{{ module_name }}(unittest.TestCase):
    def setUp(self):
        self.env = EnvManager()
        sleep(600) #TODO: add await method
        self.env.create_snapshot_env(snap_name="before_test")
{% for test in tests %}
    def test_{{ test.name }}(self):
        self.env.upload('{{ test.path }}', '{{ manifests_path }}/{{ test.file }}')
        self.env.execute_cmd("puppet apply --verbose --detailed-exitcodes --modulepath='{{ module_path }}' '{{ manifests_path }}/{{ test.file }}'")
{% endfor %}
    def tearDown(self):
        self.env.revert_snapshot_env("before_test")

if __name__ == '__main__':
    unittest.main()