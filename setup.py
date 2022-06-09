from typing import List

import setuptools


def read_multiline_as_list(file_path: str) -> List[str]:
    with open(file_path) as req_file:
        contents = req_file.read().split("\n")
        if contents[-1] == "":
            contents.pop()
        return contents


with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

requirements = read_multiline_as_list("requirements.txt")

setuptools.setup(
    name="mongow",
    version="0.0.0.2022.06.09",
    author="Teialabs",
    author_email="contato@teialabs.com",
    description="Class wrapper for mongo connections.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TeiaLabs/MongoWrapper",
    packages=setuptools.find_packages(),
    keywords='mongo motor class mixin',
    python_requires=">=3.8",
    install_requires=requirements,
)
