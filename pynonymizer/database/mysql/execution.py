import shutil
import subprocess
from pynonymizer.database.exceptions import MissingPrerequisiteError
"""
Seperate everything that touches actual query exec into its own module
"""


class MySqlDumpRunner:
    def __init__(self, db_host, db_user, db_pass, db_name):
        self.db_host = db_host
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name

        if not (shutil.which("mysqldump")):
            raise MissingPrerequisiteError("The 'mysqldump' client must be present in the $PATH")

    def __get_base_params(self):
        return ["mysqldump", "--host", self.db_host, "--user", self.db_user, f"-p{self.db_pass}"]

    def open_dumper(self):
        return subprocess.Popen(self.__get_base_params() + [self.db_name], stdout=subprocess.PIPE).stdout


class MySqlCmdRunner:
    def __init__(self, db_host, db_user, db_pass, db_name):
        self.db_host = db_host
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name

        if not (shutil.which("mysql")):
            raise MissingPrerequisiteError("The 'mysql' client must be present in the $PATH")

    def __get_base_params(self):
        return ["mysql", "-h", self.db_host, "-u", self.db_user, f"-p{self.db_pass}"]

    def execute(self, statement):
        return subprocess.check_output(self.__get_base_params() + ["--execute", statement])

    def db_execute(self, statement):
        return subprocess.check_output(self.__get_base_params() + [self.db_name,  "--execute", statement])

    def get_single_result(self, statement):
        return subprocess.check_output(self.__get_base_params() + ["-sN", self.db_name, "--execute", statement]).decode()

    def open_batch_processor(self):
        return subprocess.Popen(self.__get_base_params() + [self.db_name], stdin=subprocess.PIPE).stdin

    def test(self):
        """
        Prove a connection is viable - gives callers a fast-fail check for "did the client give me bad credentials?"
        Internally, execute some kind of easy NOOP that always works.
        :return True on success, False on Failure
        """
        try:
            self.execute("SELECT @@VERSION;")
            return True
        except subprocess.CalledProcessError:
            return False