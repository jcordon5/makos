from setuptools import find_packages, setup

setup(
    name="makos-bridge",
    version="0.1.0",
    description="Model-agnostic CLI bridge for a shared Obsidian knowledge vault",
    packages=find_packages(where="bridge"),
    package_dir={"": "bridge"},
    install_requires=[],
    extras_require={"dev": ["pytest>=8.0"]},
    entry_points={"console_scripts": ["makos=makos_bridge.cli:main"]},
    python_requires=">=3.9",
)
