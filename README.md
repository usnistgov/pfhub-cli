# PFHub CLI

A Python module for both rendering and submitting [PFHub] phase field
benchmark results using Jupyter, Pandas and Plotly.

To view benchmark results go to the live website at <strong><a href="https://pages.nist.gov/pfhub">pages.nist.gov/pfhub</a></strong>

## Installation

### Using Pip

First install a Python environment manager such as [Micromamba] and
ensure [Pip] is available. To install the PFHub CLI use,

    $ pip install git+https://github.com/usnistgov/pypfhub.git
    
### Using Nix

First install the [Nix package manager][NIX] and then enable [Flakes].
To install the PFHub CLI use,

    $ nix shell github:wd15/pypfhub
    
for just the command line tool or

    $ nix develop github:wd15/pypfhub
    
to generate an environment with Python and Jupyter available. See [the
Nix section of the development guide](./DEVELOPMENT.md#flakes) to get more help
starting out with Nix

## Usage

### Test

To test that the PFHub CLI is installed correctly use

    $ pfhub test
        
### Submit a benchmark result

Under construction.

## Contributions

Contributions are welcome. See the [development guide][DEV] to get
started.

## License

See the [NIST license](./LICENSE.md)

## Cite

If you need to cite the PFHub CLI, please see [CITATION.cff][CITE] and
cite it as follows:

> Wheeler, D., Keller, T., DeWitt, S. J., Jokisaari, A. M., Schwen, D.,
> Guyer, J. E., Aagesen, L. K., Heinonen, O. G., Tonks, M. R., Voorhees,
> P. W., Warren, J. A. (2019). *PFHub: The Phase-Field Community Hub.*
> Journal of Open Research Software, 7(1), 29. DOI:
> <http://doi.org/10.5334/jors.276>

[PFHub]: https://pages.nist.gov/pfhub
[DEV]: ./DEVELOPMENT.md
[LICENSE]: ./LICENSE.md
[CITE]: ./CITATION.cff
[NIX]: https://nixos.org/download.html
[Flakes]: https://nixos.wiki/wiki/Flakes
[Micromamba]: https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html
[Pip]: https://pip.pypa.io/en/stable/
