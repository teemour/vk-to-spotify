from os import path
from setuptools import setup


class Installer:
    def __init__(self):
        self.version = open(path.join(path.dirname(__file__), "version.txt"), "r").read()

        with open("requirements.txt", "r") as file:
            self.requirements = [require.replace("\n", "") for require in file.readlines()]

    def setup(self):
        setup(
            name="vk-to-spotify",
            version=self.version,
            install_requires=self.requirements,
            author="Yuly Maysky",
            author_email="amayakasa.work@gmail.com",
            url="https://github.com/amayakasa/vk-to-spotify",
            description="Transfer your music from VK to Spotify",
            keywords="audio python music spotify vk python3 vkontakte",
            python_requires='>=3.6'
        )


Installer().setup()
