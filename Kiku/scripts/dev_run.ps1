param([switch]$Install)
if ($Install) { irm https://astral.sh/uv/install.ps1 | iex }
if (-not (Test-Path .venv)) { uv venv .venv }
. .\.venv\Scripts\Activate.ps1
uv sync --all-extras
uv run pytest
uv run python -c "from core.logging import setup_logging; setup_logging(); import structlog; structlog.get_logger().info('boot_ok')"
