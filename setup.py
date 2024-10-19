import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="VirtuCLI",
    version="0.2",
    author="manoedinata",
    author_email="manoedinata@gmail.com",
    description="Basic management of Virtualizor VMs from CLI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manoedinata/VirtuCLI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "virtucli = virtucli.main:main",
        ],
    },
    install_requires=[
        "appdirs",
        "tabulate",
        "VirtualizorEndpoint @ git+https://github.com/manoedinata/VirtualizorEnduser-Python"
    ],
    python_requires='>=3.6',
)
