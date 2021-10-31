import os
from setuptools import find_packages, setup

data_files = []
for root, dirs, files in os.walk("configuration"):
    data_files.append(
        (os.path.relpath(root, "configuration"), [os.path.join(root, f) for f in files])
    )

setup(
    name="kle_pcbgen",
    version="0.1",
    # author=AUTHOR,
    # license=LICENSE,
    package_dir={"": "src"},
    packages=["kle_pcbgen"],
    data_files=data_files,
    python_requires=">=3.7",
    scripts=["bin/pcbgen"],
    install_requires=["Jinja2==3.0.2"],
)
