from setuptools import setup

setup(
    name='sokannonser',
    packages=['sokannonser'],
    include_package_data=True,
    install_requires=[
        'valuestore', 'flask', 'flask-restplus', 'flask-cors', 'elasticsearch', 'certifi',
        'requests'
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
