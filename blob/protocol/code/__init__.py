"""Compile and import all the protocol buffer definitions.
This code is quite hacky and should be refactored.
"""
import re
import sys
import inspect
import importlib
import pkgutil

from pathlib import Path
from typing import List, Optional

from grpc.tools import protoc
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper


def build(input: Path, output: Path, arguments: Optional[dict] = None):
    """Build all the *.proto source files from input to output."""
    arguments = (arguments or {}) | {
        "--proto_path": str(input),
        "--python_out": str(output)
        }
    arguments = sum(zip(arguments.keys(), arguments.values()), tuple())
    protoc.main(["protoc", *arguments, *map(str, input.rglob("*.proto"))])

    # Fix https://github.com/protocolbuffers/protobuf/pull/7470
    find, replace = re.compile(r"(^import .+_pb..*)"), f"from . \1"
    for path in output.rglob("*_pb*.py"):
        with open(path, "r") as file:
            fixed = re.sub(find, replace, file.read())
        with open(path, "w") as file:
            file.write(fixed)


def load(directories: List[Path]):
    """Import all the compiled *.proto definitions to the module scope."""
    for parent, name, is_package in pkgutil.iter_modules(directories):
        module = importlib.import_module("." + name, Path(parent.path).name)
        for name, item in module.__dict__.items():
            if inspect.isclass(item) or isinstance(item, EnumTypeWrapper):
                globals().update({name: item})
                yield name


directory = Path(__file__).resolve().parent
build(directory.parent, directory)
sys.path.append(str(directory))

# Roughly equivalent to `from {directory}/**/*_pb*.py import *`
__all__ = list(load(
    path if path.is_dir() else path.parent
    for path in directory.rglob("*_pb*.py")
    ))
