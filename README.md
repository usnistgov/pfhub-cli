# PFHub CLI

A Python module for both rendering and submitting [PFHub] phase field
benchmark results using Jupyter, Pandas and Plotly.

To view benchmark results go to the live website at <sup><strong><a href="https://pages.nist.gov/pfhub">pages.nist.gov/pfhub</a></strong></sup>.

## Installation

### Using Pip

To install with pip use,

    $ pip install git+https://github.com/usnistgov/pypfhub.git
    
### Using Nix

To install using Nix use,

    $ nix shell github:wd15/pypfhub
    
for just the command line tool or

    $ nix develop github:wd15/pypfhub
    
to generate an environment with Python and Jupyter available. See [the
Nix section of the development guide](./DEVELOPMENT.md#flakes) to get
started with Nix.

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
