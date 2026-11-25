from database_transfer import split_sql_statements


def test_split_sql_statements_preserves_multiline_and_quoted_semicolons():
    sql = """-- Backup header
SET FOREIGN_KEY_CHECKS=0;
CREATE TABLE `example` (
  `value` TEXT
);
INSERT INTO `example` (`value`) VALUES ('first; value'), ('it''s fine');
SET FOREIGN_KEY_CHECKS=1;
"""

    assert list(split_sql_statements(sql)) == [
        "SET FOREIGN_KEY_CHECKS=0",
        "CREATE TABLE `example` (\n  `value` TEXT\n)",
        "INSERT INTO `example` (`value`) VALUES ('first; value'), ('it''s fine')",
        "SET FOREIGN_KEY_CHECKS=1",
    ]
