from setuptools import setup, find_packages

setup(
    name="pythonrouge",
    version="0.4",
    description="ROUGE script using python",
    url="http://github.com/jimmycode/pythonrouge",
    author="Jimmy WU",
    author_email="topcoderjimmy@gmail.com",
    keywords=[
        "NL", "CL", "natural language processing", "computational linguistics",
        "summarization"
    ],
    packages=["pythonrouge"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Topic :: Text Processing :: Linguistic"
    ],
    license="LICENCE.txt",
    long_description=open("README.md").read(),)
