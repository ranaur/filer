from filer import db
from filer import tests

def test_new_creates_filebase(tmp_path):
    database = tmp_path / "test_new"

    tests.newDatabase(database)

    version  = tests.queryOne("SELECT value FROM config WHERE key='version'")
    assert version == db.SCHEMA_VERSION

    tests.deleteDatabase()