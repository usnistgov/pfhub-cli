# Development

PFHub CLI is developed using Nix. Conda / Mamba / Micromamba will also
work just fine. See the [nix.dev] to get started with Nix.

## Setup

Poetry is used to generate the development environment. The flake.nix
then uses poetry2nix to generate the Nix environment. The first step
is to generate an environment using Micromamba.

### Using Mamba from Nix

To install Micromamba using Nix follow these
[instructions][micromamba-nix]. This seems to work very well with Nix
(much better than Conda which is a real mess). In the following
Micromamba is installed via Nix's home-manager. Once installed the
following environment can be generated.

 
    $ eval "$(micromamba shell hook -s bash)"
    $ micromamba create -n pfhub python=3.10 poetry
    $ micromamba activate pfhub
    $ cd .../pfhub-cli
    
Use
 
    $ poetry install
    
to install the dependencies and install as a development package.

The PFHub CLI should be available

    $ pfhub --help
    Usage: pfhub [OPTIONS] COMMAND [ARGS]...

To add new packages use (don't edit `pyproject.toml` by hand).

    $ poetry add package
    
    
### Building Nix installatioin using Poetry

The current Nix environment uses poetry2nix to build the
environment. If the environment needs updating run


    $ poerty lock
    $ poetry install
    
first bofore running
    
    $ nix develop

and then run the CLI with

    $ pfhub --help
    
To run the CLI directly use

    $ nix run .#pfhub -- --help

## Additional odds and ends

### Nix Shell Prompt

**NOTE**: the `nix develop` command fails to change the shell prompt
to indicate that you are now in a Nix environment. To remedy this add
the following to your `~/.bashrc`.

```
show_nix_env() {
  if [[ -n "$IN_NIX_SHELL" ]]; then
    echo "(nix)"
  fi
}
export -f show_nix_env
export PS1="\[\e[1;34m\]\$(show_nix_env)\[\e[m\]"$PS1
```

### Flakes

The PFHub Nix expressions use an experimental feature known as flakes,
see the [official flake documentation][flakes].

To enable Nix flakes, add a one liner to either
`~/.config/nix/nix.conf` or `/etc/nix/nix.conf`. The one liner is

```
experimental-features = nix-command flakes
```

If you need more help consult [this
tutorial](https://www.tweag.io/blog/2020-05-25-flakes/).

To test that flakes are working try

    $ nix flake metadata github:usnistgov/pfhub-cli
    Resolved URL:  github:usnistgov/pfhub-cli
    ...
        └───systems: github:nix-systems/default/da67096a3b9bf56a91d16901293e51ba5b49a27e

### Update Flakes

    $ nix flake update
    $ nix develop

When the flake is updated, a new `flake.lock` file is generated which
must be committed to the repository alongside the `flake.nix`. Note
that the flake files depend on the `nixos-23.05` branch which is only
updated with backports for bug fixes. To update to a newer version of
Nixpkgs then the `flake.nix` file requires editing to point at a later
Nixpkgs version.

### Commit messages

Use [conventional commits][conventional]. A commit message should look
like

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

where the type is from the following list

```
[
  'build',
  'chore',
  'ci',
  'docs',
  'feat',
  'fix',
  'perf',
  'refactor',
  'revert',
  'style',
  'test'
]
```
    
### Pushing to PyPI test

See this [Stackoverflow question][pypi-test] for some help.

Configure with

   $ poetry config repositories.test-pypi https://test.pypi.org/legacy/
   $ poetry config pypi-token.pypi <TOKEN>
   
To publish use

   $ poetry build
   $ poetry publish -r test-pypi
   
[nix.dev]: https://nix.dev
[micromamba-nix]: https://nixos.wiki/wiki/Python#micromamba
[flakes]: https://nixos.wiki/wiki/Flakes
[conventional]: https://www.conventionalcommits.org
[pypi-test]: https://stackoverflow.com/questions/68882603/using-python-poetry-to-publish-to-test-pypi-org
