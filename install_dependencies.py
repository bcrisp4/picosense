import mip

dependencies = [
    {
        "name": "typing",
        "authors": ["micropython-stubs"],
        "homepage": "https://github.com/Josverl/micropython-stubs/tree/main/mip",
        "url": "github:josverl/micropython-stubs/mip/typing.mpy",
    },
    {
        "name": "typing_extensions",
        "authors": ["micropython-stubs"],
        "homepage": "https://github.com/micropython/micropython-lib/tree/master/python-stdlib/logging",
        "url": "github:josverl/micropython-stubs/mip/typing_extensions.mpy",
    },
    {
        "name": "ntptime",
        "authors": ["micropython-lib"],
        "homepage": "https://github.com/micropython/micropython-lib/tree/master/micropython/net/ntptime",
        "url": "ntptime",
    },
    {
        "name": "logging",
        "authors": ["micropython-lib"],
        "homepage": "https://github.com/micropython/micropython-lib/tree/master/python-stdlib/logging",
        "url": "logging",
    },
    {
        "name": "time",
        "authors": ["micropython-lib"],
        "homepage": "https://github.com/micropython/micropython-lib/tree/master/python-stdlib/time",
        "url": "time",
    },
    {
        "name": "umqtt",
        "authors": ["micropython-lib"],
        "homepage": "https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.simple",
        "url": "umqtt.simple",
    },
    {
        "name": "bh1750",
        "authors": ["flrrth"],
        "homepage": "https://github.com/flrrth/pico-bh1750",
        "url": "https://raw.githubusercontent.com/flrrth/pico-bh1750/04493a20ccef2babe4cb457dd2f1e2fdecc50433/bh1750/bh1750.py",
    },
    {
        "name": "bme688",
        "authors": ["Limor Fried", "CRCibernetica"],
        "homepage": "https://github.com/CRCibernetica/bme688-i2c-micropython",
        "url": "https://raw.githubusercontent.com/CRCibernetica/bme688-i2c-micropython/07a7b9fb775ef4466fe3e65e03f95dfd740be676/bme688.py",
    },
    {
        "name": "scd4x",
        "authors": ["Scott Shawcroft", "peter-l5"],
        "homepage": "https://github.com/peter-l5/MicroPython_SCD4X",
        "url": "https://raw.githubusercontent.com/peter-l5/MicroPython_SCD4X/e67d8202b353e4870f2efc6b19792ee4c10d584c/scd4x.py",
    },
]

for dependency in dependencies:
    print(f"Installing {dependency['name']}...")
    print(f"Authors: {', '.join(dependency['authors'])}")
    print(f"Homepage: {dependency['homepage']}")
    mip.install(dependency["url"])
