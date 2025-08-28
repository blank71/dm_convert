```bash
protoc --proto_path=. --python_out=. clientanalytics_dmc.proto timestamp.proto convert_usage.proto convert_usage_extension.proto

# Install dependencies without updating lock file.
uv sync --locked

# Exec entry point.
uv run dm_convert.py
```
