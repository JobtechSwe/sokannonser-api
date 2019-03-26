from setuptools import setup, find_packages

setup(
    name='sokannonser',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'valuestore', 'jobtech-common', 'flask', 'flask-restplus', 'flask-cors', 'elasticsearch', 'certifi',
        'requests'
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
