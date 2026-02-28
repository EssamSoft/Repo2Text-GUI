from setuptools import setup

setup(
    name="rtt",
    version="1.0.0",
    description="Repo to Text — convert repository code to AI-friendly text",
    py_modules=["rtt"],
    entry_points={
        "console_scripts": [
            "rtt=rtt:main",
        ],
    },
    python_requires=">=3.6",
)
