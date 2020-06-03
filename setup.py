import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="InMemoryDatastore",
    version="0.0.1",
    description="An in-memory stub implementation of Google Cloud Datastore",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires=">=3",
    install_requires=["google-cloud-ndb == 1.2.1"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "black", "pyre-check", "flake8", "grpc-stubs"],
)
