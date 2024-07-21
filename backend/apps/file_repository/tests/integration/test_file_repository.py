import os.path
from unittest import TestCase
from unittest.mock import patch

from apps.file_repository.services import services
from apps.file_repository.tests.integration.config import report_template_test_data
from apps.user.models import User

TEST_USER = None


@patch('apps.file_repository.services.services._save_file', return_value=['dummyfile', 'jpg'])
class TestFileRepository(TestCase):
    def test_add_file(self, _):
        with open(os.path.join(os.path.dirname(__file__), 'dummy_file.txt'), encoding='utf8') as report_file:
            test_user = User.objects.get(username='admin')
            services.delete_file()
            services.add_file(data=report_template_test_data, report_file=report_file, user=test_user)
