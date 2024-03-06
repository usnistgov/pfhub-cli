# Development

PFHub CLI is developed using Nix. Conda / Mamba / Micromamba will also
work just fine. See the [nix.dev] to get started with Nix.

## Setup

Poetry is used to generate the development environment. The flake.nix
then uses poetry2nix to generate the Nix environment. The first step
is to generate an environment using Micromamba.

### Using Mamba from Nix

To install Micromamba using Nix follow these
[instructions][micromamba-nix]. This seems to work very well with Nix.
In the following Micromamba is installed via Nix's home-manager.
Once installed the following environment can be generated.

    $ eval "$(micromamba shell hook -s ${SHELL})"
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
    
### Building Nix installation using Poetry

The current Nix environment uses poetry2nix to build the
environment. If the environment needs updating run

    $ poetry lock
    $ poetry install
    
first before running

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

``` bash
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

``` text
experimental-features = nix-command flakes
```

If you need more help consult [this
tutorial](https://www.tweag.io/blog/2020-05-25-flakes/).

To test that flakes are working try

    $ nix flake metadata github:usnistgov/pfhub-cli
    Resolved URL:  github:usnistgov/pfhub-cli
    ⁞
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

    <type>[optional scope]: <description>

    [optional body]

    [optional footer]

where the `type` is one of the following:

- `build` — build system configuration
- `chore` — tedious work
- `ci` — continuous integration configuration
- `docs` — documentation edits
- `feat` — adding or modifying a feature
- `fix` — fixing a bug
- `perf` — performance improvements
- `refactor` — refactoring a chunk of code
- `revert` — undo a previous commit
- `style` — stylistic changes
- `test` — test system configuration

### Pushing to PyPI test

See this [StackOverflow question][pypi-test] for some help.

Configure with

    $ poetry config repositories.test-pypi https://test.pypi.org/legacy/
    $ poetry config pypi-token.pypi <TOKEN>
   
To publish, use

    $ poetry build
    $ poetry publish -r test-pypi
   
[nix.dev]: https://nix.dev
[micromamba-nix]: https://nixos.wiki/wiki/Python#micromamba
[flakes]: https://nixos.wiki/wiki/Flakes
[conventional]: https://www.conventionalcommits.org
[pypi-test]: https://stackoverflow.com/questions/68882603/using-python-poetry-to-publish-to-test-pypi-org

### Deploying the docs

Use

    $ mkdocs gh-deploy --remote-branch nist-pages --remote-name upstream

when in the nix development environment. This will build the docs and
push to the `nist-pages` branch in the upstream repository.



### Setting up Zenodo

It's best to start testing uploads using Zenodo Sandbox before using
the main Zenodo repository. See [the zenodo-client
documentation](https://pypi.org/project/zenodo-client/) for more
details, but the following steps should work:

 - Create an account with Zenodo sandbox at
   [https://sandbox.zenodo.org/signup/](https://sandbox.zenodo.org/signup/).
   
 - Generate a Zenodo token from
   [https://sandbox.zenodo.org/account/settings/applications/](https://sandbox.zenodo.org/account/settings/applications/)
   under "Applications" > "Personal Access Tokens". Select
   "deposits:actions", "deposits:write" and "user:email" when
   generating the token.
   
 - Copy the token and set the `ZENODO_SANDBOX_API_TOKEN` environment
   variable using the token or add the token to `~/.config/zenodo.ini`
   so that it looks like

```
[zenodo]
sandbox_api_token = XXX

```

 - Test using the PFHub CLI to upload data to Zenodo Sandbox. Use
   `pfhub upload pfhub.yaml --sandbox` to do this. Sample data is
   available here
   [here](https://github.com/usnistgov/pfhub-cli/tree/main/pfhub/test_data).
 
 
**NOTE**: logging into Zenodo's sandbox can be difficult with ORCID
and is probably easier with a GitHub ID.

To use the main Zenodo repository (not sandbox), follow the same
instructions as above, but use the main Zenodo site. Set the
`ZENODO_API_TOKEN` or add the `api_token = XXX` to
`~/.config/zenodo.ini`.

