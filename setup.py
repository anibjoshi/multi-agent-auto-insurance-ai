from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multi-agent-auto-insurance-ai",
    version="1.0.0",
    author="Auto Insurance AI Team",
    author_email="team@autoinsurance.ai",
    description="Production-grade multi-agent AI system for auto insurance claim processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/multi-agent-auto-insurance-ai",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "claim-processor-api=api.main:app",
            "claim-processor-demo=scripts.demo:main",
            "claim-processor-test=tests.test_system:main",
        ],
    },
    include_package_data=True,
    package_data={
        "claim_processor": ["py.typed"],
    },
    zip_safe=False,
) 