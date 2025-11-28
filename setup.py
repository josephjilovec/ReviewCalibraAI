from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="reviewcalibraai",
    version="0.1.1",                    # bumped so pip notices the change
    author="Joseph Jilovec",
    description="Transparent reviewer-to-paper matching for conference peer review",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="."),   # ← critical fix
    package_dir={"": "."},               # ← tells it the packages are in the root
    include_package_data=True,
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "test": ["pytest>=7.0", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "reviewcalibraai = scripts.main:main",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
