import string
import random
import getpass
from omnidump.cli import show
class TestShowFail:

    def test_show_owner_2(self, cli_runner, owner_base_args):
        args = owner_base_args

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 2
        assert "Error: Option '--owner' requires an argument." in result.output
    
    def test_show_owner_16(self, cli_runner, owner_base_args):
        length = 8
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        args = owner_base_args + [random_string]

        result = cli_runner.invoke(show, args)
        error_message = f"Showing processes...\nError: The user '{random_string}' doesn't exist.\n"
        assert result.exit_code == 16
        assert error_message in result.output

class TestShowPass:

    def test_show_owner_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_owner_sleeping_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-sp"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0
    
    def test_show_owner_idle_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-id"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0
    
    def test_show_owner_running_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-rn"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_owner_sleeping_idle_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-sp", "-id"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_owner_sleeping_idle_running_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-sp", "-id", "-rn"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_sleeping_pass(self, cli_runner):
        args = ["-sp"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_sleeping_running_pass(self, cli_runner):
        args = ["-sp", "-rn"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_sleeping_running_idle_pass(self, cli_runner):
        args = ["-sp", "-rn", "-id"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_idle_pass(self, cli_runner):
        args = ["-id"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_idle_running_pass(self, cli_runner):
        args = ["-id", "-rn"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_running_pass(self, cli_runner):
        args = ["-rn"]
        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0
