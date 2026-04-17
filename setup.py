from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="automated-book-generation",
    version="1.0.0",
    author="AI Developer",
    author_email="developer@example.com",
    description="A professional full-stack AI-powered system for automated book generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/automated-book-generation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Office/Business :: Office Suites",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "book-gen-server=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["*.py"],
    },
)
