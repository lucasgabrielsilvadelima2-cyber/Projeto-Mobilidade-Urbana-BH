"""Setup configuration for BH Mobilidade Urbana Pipeline."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bh-mobilidade-pipeline",
    version="1.0.0",
    author="BeAnalytic Data Team",
    description="Pipeline de dados de mobilidade urbana de Belo Horizonte",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/beanalytic/bh-mobilidade-pipeline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Data Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pandas>=2.1.0",
        "pyarrow>=14.0.0",
        "requests>=2.31.0",
        "great-expectations>=0.18.0",
        "pandera>=0.17.0",
        "deltalake>=0.15.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "tqdm>=4.66.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "pyspark": [
            "pyspark>=3.5.0",
        ],
    },
)
