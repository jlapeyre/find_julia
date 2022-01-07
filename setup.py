import setuptools

version = {}
with open("./find_julia/_version.py") as fp:
    exec(fp.read(), version)

setuptools.setup(
    name='find_julia',
    version=version['__version__'],
    description='Manage a Julia project inside a Python package',
    url='https://github.com/jlapeyre/find_julia.git',
    author='John Lapeyre',
    license = 'MIT',
    packages=setuptools.find_packages(),
    py_modules=["find_julia", ],
    install_requires=['jill'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    # extras_require={
    #     "test": [
    #         "pytest",
    #         "mock",
    #     ],
    # },
)
