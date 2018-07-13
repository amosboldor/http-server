"""Setup for http-server."""

from setuptools import setup


setup(
    name="http-server",
    description="Implementations of a simple http server.",
    version=0.2,
    install_requires=[
        "gevent"
    ],
    author="Amos Boldor",
    author_email='amosboldor@gmail.com',
    license="MIT",
    package_dir={'': 'src'},
    py_modules=['server', 'client'],
    extras_require={
        "test": ["pytest", "pytest-watch", "pytest-cov", "tox"]
    },
    entry_points={
        'console_scripts': [
            'client = client:client',
            'server = server:run_server'
        ]
    }
)
