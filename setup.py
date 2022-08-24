import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='MicroPython-ADE7878A',
    version='0.0.1',
    author='Submer Inc',
    description='MicroPython driver for ADE7878A energy metering IC',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/submer-crypto/MicroPython-ADE7878A',
    license='ISC',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Topic :: System :: Hardware'
    ],
    python_requires='>=3.9',
)
