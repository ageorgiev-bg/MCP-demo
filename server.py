#!/usr/bin/env python3
"""
Simple MCP server to query DB for user data.
"""

import psycopg2
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("Get_User_Data_MCP_server")


def db_connection(host, port, dbname, usr, pwd):
    conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=usr, password=pwd)
    return conn


@mcp.tool()
def get_user_data(user_id):
    """Finds a user record in the database.

    Args:
        user_id: The user's ID to look up.

    Returns:
        A dict of the user's data, or an empty dict if not found.
    """
    read_user_data = """
        SELECT * FROM users WHERE user_id = %s
    """
    host = "postgres"  # resolves via Podman's internal DNS
    port = 5432
    dbname = "postgres"
    usr = "postgres"
    pwd = "postgres"  # TODO: load from  os.environ["DB_PASSWORD"]

    dbconn = None
    cur = None
    try:
        dbconn = db_connection(host, port, dbname, usr, pwd)
        cur = dbconn.cursor()
        cur.execute(read_user_data, (user_id,))
        rows = cur.fetchall()

        if not rows:
            return {}

        columns = [desc[0] for desc in cur.description]
        user_data = dict(zip(columns, rows[0]))
        return user_data
    except Exception as e:
        raise RuntimeError(f"Failed to fetch user data: {e}")
    finally:
        if cur:
            cur.close()
        if dbconn:
            dbconn.close()


if __name__ == "__main__":
    # FastMCP doesn't support transport_options parameter, session timeout is handled by the underlying transport layer
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
