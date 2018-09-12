
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scgv",
    version="1.0.1",
    author="Lubomir Chorbadjiev",
    author_email="lubomir.chorbadjiev@gmail.com",
    description="SCGV is an interacive graphical tool for single-cell genomics data, with emphasis on single-cell genomics of cancer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KrasnitzLab/SCGV",
    packages=setuptools.find_packages(
        # 'scgv',
        exclude=['docs', 'tests']
    ),
    # package_dir={'':'scgv'},
    entry_points={
        'console_scripts': [
            'scgview=scgv.tkmain:main',
        ]
    },
    classifiers=(
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    python_requires='>=3.6',
    
)