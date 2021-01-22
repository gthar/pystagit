from setuptools import setup


def readme():
    with open("README.md") as fh:
        return fh.read()


setup(
    name="pystagit",
    version="0.1",
    description="static page generator for git written in python",
    long_description=readme(),
    url="https://git.monotremata.xyz/pystagit",
    author="Ricard Illa",
    author_email="rilla@monotremata.xyz",
    license="MIT",
    packages=["pystagit"],
    install_requires=["markdown", "jinja2", "pygit2", "pygments"],
    zip_safe=False,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pystagit-index=pystagit.pystagit_index:main",
            "pystagit=pystagit.pystagit:main",
        ]
    },
)
