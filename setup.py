import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ustjson-huge-yellow-dog",
    version="1.1.0",
    author="jiyang",
    author_email="jiyangj@foxmail.com",
    description="Unstructured terms text to JSON.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JIYANG-PLUS/ustjson",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)