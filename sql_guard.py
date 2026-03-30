def is_safe_sql(query: str) -> bool:
    if not query:
        return False

    q = query.strip().upper()

    # ❌ Block multiple statements
    if q.count(";") > 1:
        return False

    # ❌ Block extremely dangerous commands
    blocked_keywords = [
        "DROP DATABASE",
        "DROP TABLE",
        "TRUNCATE",
        "CREATE DATABASE"
    ]

    for word in blocked_keywords:
        if word in q:
            return False

    # ✅ Allowed starting keywords
    allowed_starts = ("SELECT", "INSERT", "UPDATE", "DELETE", "ALTER")

    if not q.startswith(allowed_starts):
        return False

    # ⚠️ UPDATE and DELETE must have WHERE
    if q.startswith("UPDATE") and "WHERE" not in q:
        return False

    if q.startswith("DELETE") and "WHERE" not in q:
        return False

    # ⚠️ ALTER allowed only for ADD or MODIFY
    if q.startswith("ALTER"):
        if not (" ADD " in q or " MODIFY " in q):
            return False

    return True