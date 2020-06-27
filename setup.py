import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="InMemoryCloudDatastoreStub",
    version="0.0.6",
    description="An in-memory stub implementation of Google Cloud Datastore for use in unit tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phil-lopreiato/google-cloud-datastore-stub/",
    packages=setuptools.find_packages(),
    python_requires=">=3",
    install_requires=["google-cloud-ndb == 1.2.1"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "black", "pyre-check", "flake8", "mypy"],
)
