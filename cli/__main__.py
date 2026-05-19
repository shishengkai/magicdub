import sys

if len(sys.argv) > 1 and sys.argv[1] == "provider":
    from cli.provider import app

    sys.argv.pop(1)
    app(prog_name="python -m cli provider")
else:
    from cli.main import app

    app()
