from setuptools import setup, find_packages

setup(
    name="ai4ia.stardist",
    packages=find_packages(),
    version="0.0.1",
    author="Constantin Pape, Christian Tischer",
    url="https://git.embl.de/grp-bio-it/ai4ia.git",
    license='MIT',
    entry_points={
        "console_scripts": [
            "train_stardist_2d = stardist_impl.train_stardist_2d:main",
            "predict_stardist_2d = stardist_impl.predict_stardist_2d:main",
            "train_stardist_3d = stardist_impl.train_stardist_3d:main",
            "predict_stardist_3d = stardist_impl.predict_stardist_3d:main",
            "stardist_model_to_fiji = stardist_impl.stardist_model_to_fiji:main"
        ]
    },
)
