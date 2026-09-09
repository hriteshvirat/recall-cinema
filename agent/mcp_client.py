import os
import sys
import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from backend.app.config import settings
from backend.app.logger import logger, log_operation
from backend.app.models import TraceStep

class ClickHouseMCPClient:
    """
    Client interface connecting to the official ClickHouse MCP server (mcp-clickhouse).
    Executes real tool calls (run_query, list_tables, list_databases) across the
    standard Model Context Protocol transport and captures authentic telemetry.
    """

    def __init__(self):
        self.host = settings.CLICKHOUSE_HOST
        self.port = settings.CLICKHOUSE_PORT
        self.user = settings.CLICKHOUSE_USER
        self.password = settings.CLICKHOUSE_PASSWORD
        self.database = settings.CLICKHOUSE_DATABASE
        self.secure = settings.CLICKHOUSE_SECURE

    def get_server_env(self) -> Dict[str, str]:
        env = dict(os.environ)
        env.update({
            "CLICKHOUSE_HOST": self.host,
            "CLICKHOUSE_PORT": str(self.port),
            "CLICKHOUSE_USER": self.user,
            "CLICKHOUSE_PASSWORD": self.password,
            "CLICKHOUSE_DATABASE": self.database,
            "CLICKHOUSE_SECURE": "true" if self.secure else "false",
        })
        return env

    async def _execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, float]:
        """
        Executes a tool call on the official mcp-clickhouse server over stdio.
        Measures exact runtime latency.
        """
        start_time = time.time()
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        # Find executable path for mcp-clickhouse or run via python -m
        env = self.get_server_env()
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_clickhouse"],
            env=env
        )

        try:
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=arguments)
                    elapsed_ms = (time.time() - start_time) * 1000
                    return result, elapsed_ms
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"MCP tool call '{tool_name}' failed after {elapsed_ms:.1f}ms: {e}")
            raise

    def run_query(self, query: str) -> Tuple[List[Dict[str, Any]], TraceStep]:
        """
        Synchronously calls the MCP tool 'run_query' (or 'run_select_query')
        and returns parsed row dictionaries along with real MCP telemetry.
        """
        start_time = time.time()
        logger.info(f"[ClickHouse MCP] Executing query over MCP: {query}")

        # Clean query
        clean_query = query.strip().rstrip(";")

        try:
            # We attempt standard MCP tool call
            # mcp-clickhouse supports run_query / run_select_query
            tool_name = "run_query"
            arguments = {"query": clean_query}

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                mcp_result, elapsed_ms = loop.run_until_complete(
                    self._execute_mcp_tool(tool_name, arguments)
                )
            finally:
                loop.close()

            # Parse content from MCP tool response
            raw_text = ""
            if hasattr(mcp_result, "content") and mcp_result.content:
                for item in mcp_result.content:
                    if hasattr(item, "text"):
                        raw_text += item.text

            # Parse JSON or tabular output from MCP
            rows = []
            if raw_text:
                try:
                    parsed = json.loads(raw_text)
                    if isinstance(parsed, list):
                        rows = parsed
                    elif isinstance(parsed, dict) and "data" in parsed:
                        rows = parsed["data"]
                    else:
                        rows = [parsed]
                except Exception:
                    # Tabular text format fallback
                    lines = [ln.strip() for ln in raw_text.split("\n") if ln.strip()]
                    rows = [{"raw_output": ln} for ln in lines]

            trace = TraceStep(
                stage="ClickHouse MCP run_query",
                detail=f"Executed via official mcp-clickhouse on {self.host}:{self.port}",
                mcp_tool=tool_name,
                sql_query=clean_query,
                rows_returned=len(rows),
                duration_ms=round(elapsed_ms, 2)
            )

            log_operation(
                "mcp_run_query",
                duration_ms=elapsed_ms,
                success=True,
                extra={"query": clean_query, "rows": len(rows), "tool": tool_name}
            )
            return rows, trace

        except Exception as e:
            # If the stdio process fails (e.g. host unreachable or bad query), capture error in trace
            elapsed_ms = (time.time() - start_time) * 1000
            trace = TraceStep(
                stage="ClickHouse MCP run_query (Error)",
                detail=f"MCP Error: {str(e)}",
                mcp_tool="run_query",
                sql_query=clean_query,
                rows_returned=0,
                duration_ms=round(elapsed_ms, 2)
            )
            log_operation(
                "mcp_run_query",
                duration_ms=elapsed_ms,
                success=False,
                error=str(e),
                extra={"query": clean_query}
            )
            raise RuntimeError(f"ClickHouse MCP server execution failed: {e}") from e

    def list_tables(self) -> Tuple[List[str], TraceStep]:
        """Calls list_tables tool on MCP server."""
        start_time = time.time()
        tool_name = "list_tables"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            mcp_result, elapsed_ms = loop.run_until_complete(
                self._execute_mcp_tool(tool_name, {})
            )
        finally:
            loop.close()

        tables = []
        if hasattr(mcp_result, "content") and mcp_result.content:
            for item in mcp_result.content:
                if hasattr(item, "text"):
                    tables.append(item.text)

        trace = TraceStep(
            stage="ClickHouse MCP list_tables",
            detail=f"Inspected schema via mcp-clickhouse",
            mcp_tool=tool_name,
            rows_returned=len(tables),
            duration_ms=round(elapsed_ms, 2)
        )
        return tables, trace

mcp_client = ClickHouseMCPClient()
