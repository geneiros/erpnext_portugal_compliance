from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in erpnext_portugal/__init__.py
from erpnext_portugal import __version__ as version

setup(
    name="erpnext_portugal",
    version=version,
    description="Cumprimento da legislação fiscal portuguesa para Frappe / ERPNext v16",
    author="Helder",
    author_email="helder@example.com",
    license="Apache-2.0",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
