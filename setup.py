from setuptools import setup

setup(
    name="pythonrouge",
    version="0.4",
    description="ROUGE script using python",
    url="http://github.com/jimmycode/pythonrouge",
    author="Jimmy WU",
    author_email="topcoderjimmy@gmail.com",
    keywords=["NL", "CL", "natural language processing", "computational linguistics", "summarization"],
    packages=["pythonrouge"],
    package_data={
        'pythonrouge': ['RELEASE-1.5.5/*.*',
              'RELEASE-1.5.5/data/smart_common_words.txt',
              'RELEASE-1.5.5/data/WordNet-1.6.exc.db',
              'RELEASE-1.5.5/data/WordNet-2.0.exc.db',
              'RELEASE-1.5.5/data/WordNet-1.6-Exceptions/*.*',
              'RELEASE-1.5.5/data/WordNet-2.0-Exceptions/*.*',
              ],
        },
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Linguistic"
        ],
    license="LICENCE.txt",
    long_description=open("README.md").read(),
)
