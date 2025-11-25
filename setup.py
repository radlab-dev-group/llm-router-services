import pathlib
from setuptools import setup, find_packages


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def read_version() -> str:
    """Read the project version from the .version file."""
    version_file = pathlib.Path(__file__).with_name(".version")
    return version_file.read_text(encoding="utf-8").strip()


def read_long_description() -> str:
    """Read README.md for the long description (fallback to empty string)."""
    readme_file = pathlib.Path(__file__).with_name("README.md")
    return readme_file.read_text(encoding="utf-8") if readme_file.is_file() else ""


def parse_requirements() -> list[str]:
    """Parse requirements.txt into a list suitable for install_requires."""
    req_file = pathlib.Path(__file__).with_name("requirements.txt")
    if not req_file.is_file():
        return []
    return [
        line.strip()
        for line in req_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


# ----------------------------------------------------------------------
# Setup configuration
# ----------------------------------------------------------------------
setup(
    name="llm_router_services",
    version=read_version(),
    description="HTTP services for LLM‑Router plugins (guardrails, maskers, etc.)",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="RadLab.dev Team",
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
)
