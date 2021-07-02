# Python SDK for Mesh

[![GitHub pages](https://github.com/PowelAS/sme-mesh-python/actions/workflows/pages.yml/badge.svg)](https://github.com/PowelAS/sme-mesh-python/actions/workflows/pages.yml)  [![Build and test](https://github.com/PowelAS/sme-mesh-python/actions/workflows/build_and_test.yml/badge.svg)](https://github.com/PowelAS/sme-mesh-python/actions/workflows/build_and_test.yml)

`volue.mesh` is a **work in progress** Python library that can be used to
communicate with Volue Energy's Mesh server.

Installation:

```
> python -m pip install git+https://github.com/PowelAS/sme-mesh-python
```

Examples:

```
> python examples/mesh/1_get_version.py
Server: Volue Mesh Server 1.12.5.0-dev (2021-04-26 ae939aef)
Client: 0.0.0
```

[Online documentation](https://vigilant-eureka-e3845ca2.pages.github.io/)


## Developing

This library uses [Poetry][] for development, installation, and packaging. To
work with the repository you should [install poetry][poetry-install].

After installation you can run `poetry install` to install all our
development and runtime dependencies to a virtual environment, as well as
`poetry build` to create a package.

`poetry build` will also (re)generate our grpc/protobuf sources, and should
be ran after changes to those.

To run arbitrary commands in the Poetry environment run `poetry run $command`,
or use `poetry shell` to drop into a shell with the dependencies available.

For example to run the GetVersion example you'd run:

```
poetry run python examples/mesh/1_get_version.py
```

[Poetry]: https://python-poetry.org/docs/
[poetry-install]: https://python-poetry.org/docs/#installation
