## 1.0

### 1.1.0

([full changelog](https://github.com/jupyterhub/nbgitpuller/compare/1.0.2...1.1.0))

#### Enhancements made

- Add retrolab support to link generator [#225](https://github.com/jupyterhub/nbgitpuller/pull/225) ([@yuvipanda](https://github.com/yuvipanda))

#### Bugs fixed

- Fix sync problems after deleting files [#257](https://github.com/jupyterhub/nbgitpuller/pull/257) ([@jdmansour](https://github.com/jdmansour))
- Use our own jinja2 template loader [#255](https://github.com/jupyterhub/nbgitpuller/pull/255) ([@yuvipanda](https://github.com/yuvipanda))

#### Maintenance and upkeep improvements

- Remove binder folder with link_generator.ipynb [#249](https://github.com/jupyterhub/nbgitpuller/pull/249) ([@consideRatio](https://github.com/consideRatio))
- Use async/await instead of gen.coroutine/yield [#246](https://github.com/jupyterhub/nbgitpuller/pull/246) ([@consideRatio](https://github.com/consideRatio))

#### Documentation improvements

- Fix note format [#250](https://github.com/jupyterhub/nbgitpuller/pull/250) ([@brian-rose](https://github.com/brian-rose))
- docs: adds docstrings (refactor: rename local parameter) [#242](https://github.com/jupyterhub/nbgitpuller/pull/242) ([@consideRatio](https://github.com/consideRatio))
- DOC: Add link gen. screenshot, update example gif [#238](https://github.com/jupyterhub/nbgitpuller/pull/238) ([@consideRatio](https://github.com/consideRatio))
- Update docs and remove unnecessary Sphinx configuration files [#237](https://github.com/jupyterhub/nbgitpuller/pull/237) ([@choldgraf](https://github.com/choldgraf))
- Point people to the browser extension [#231](https://github.com/jupyterhub/nbgitpuller/pull/231) ([@yuvipanda](https://github.com/yuvipanda))

#### Other merged PRs

- ci: test against python 3.7-3.10 [#245](https://github.com/jupyterhub/nbgitpuller/pull/245) ([@consideRatio](https://github.com/consideRatio))
- Build docs using GitHub Actions, add linkcheck, and small tweaks to CI system [#232](https://github.com/jupyterhub/nbgitpuller/pull/232) ([@yuvipanda](https://github.com/yuvipanda))
- Fix conf.py to work on newer versions of sphinx [#226](https://github.com/jupyterhub/nbgitpuller/pull/226) ([@yuvipanda](https://github.com/yuvipanda))
- npm: auto-rebuild dist if js changed [#222](https://github.com/jupyterhub/nbgitpuller/pull/222) ([@manics](https://github.com/manics))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/nbgitpuller/graphs/contributors?from=2021-09-02&to=2022-03-18&type=c))

[@akhmerov](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Aakhmerov+updated%3A2021-09-02..2022-03-18&type=Issues) | [@brian-rose](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Abrian-rose+updated%3A2021-09-02..2022-03-18&type=Issues) | [@choldgraf](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Acholdgraf+updated%3A2021-09-02..2022-03-18&type=Issues) | [@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3AconsideRatio+updated%3A2021-09-02..2022-03-18&type=Issues) | [@jameshowison](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Ajameshowison+updated%3A2021-09-02..2022-03-18&type=Issues) | [@jdmansour](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Ajdmansour+updated%3A2021-09-02..2022-03-18&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Amanics+updated%3A2021-09-02..2022-03-18&type=Issues) | [@ryanlovett](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Aryanlovett+updated%3A2021-09-02..2022-03-18&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Awelcome+updated%3A2021-09-02..2022-03-18&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Ayuvipanda+updated%3A2021-09-02..2022-03-18&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3AZsailer+updated%3A2021-09-02..2022-03-18&type=Issues)

### 1.0.2 - 2021-09-03

A release to fix an issue that stopped us from publishing nbgitpuller on
conda-forge.

#### Maintenance and upkeep improvements

- Fix jupyter-packaging reference, use - instead of \_ [#219](https://github.com/jupyterhub/nbgitpuller/pull/219) ([@consideRatio](https://github.com/consideRatio))

### 1.0.1 - 2021-09-02

This release fixes a failure to install from a source distribution of the
package without having `node` and `npm` installed.

#### Maintenance and upkeep improvements

- Remove six from dev-requirements.txt [#213](https://github.com/jupyterhub/nbgitpuller/pull/213) ([@consideRatio](https://github.com/consideRatio))
- Slim package.json to avoid fields relevant to npm publication [#212](https://github.com/jupyterhub/nbgitpuller/pull/212) ([@consideRatio](https://github.com/consideRatio))
- Use jupyter-packaging for npm build [#211](https://github.com/jupyterhub/nbgitpuller/pull/211) ([@manics](https://github.com/manics))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/nbgitpuller/graphs/contributors?from=2021-09-01&to=2021-09-02&type=c))

[@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3AconsideRatio+updated%3A2021-09-01..2021-09-02&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Amanics+updated%3A2021-09-01..2021-09-02&type=Issues)

### 1.0.0 - 2021-09-01

This is not a breaking release, we have just decided to let this be 1.0.0 to
better communicate changes via the version number in future releases.

#### Enhancements made

- Support use with jupyter_server by decoupling notebook dependencies [#193](https://github.com/jupyterhub/nbgitpuller/pull/193) ([@GeorgianaElena](https://github.com/GeorgianaElena))

#### Bugs fixed

- Use addon instead of term when calling fit and import xterm css [#197](https://github.com/jupyterhub/nbgitpuller/pull/197) ([@GeorgianaElena](https://github.com/GeorgianaElena))

#### Maintenance and upkeep improvements

- Rename nbgitpuller repo's master branch to main [#189](https://github.com/jupyterhub/nbgitpuller/pull/189) ([@consideRatio](https://github.com/consideRatio))

#### Documentation improvements

- Update contributing guide to use `git-pull` [#202](https://github.com/jupyterhub/nbgitpuller/pull/202) ([@fperez](https://github.com/fperez))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/nbgitpuller/graphs/contributors?from=2021-06-24&to=2021-08-31&type=c))

[@choldgraf](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Acholdgraf+updated%3A2021-06-24..2021-08-31&type=Issues) | [@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3AconsideRatio+updated%3A2021-06-24..2021-08-31&type=Issues) | [@fmaussion](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Afmaussion+updated%3A2021-06-24..2021-08-31&type=Issues) | [@fperez](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Afperez+updated%3A2021-06-24..2021-08-31&type=Issues) | [@GeorgianaElena](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3AGeorgianaElena+updated%3A2021-06-24..2021-08-31&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Amanics+updated%3A2021-06-24..2021-08-31&type=Issues) | [@nibheis](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Anibheis+updated%3A2021-06-24..2021-08-31&type=Issues) | [@TimoRoth](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3ATimoRoth+updated%3A2021-06-24..2021-08-31&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Awelcome+updated%3A2021-06-24..2021-08-31&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Ayuvipanda+updated%3A2021-06-24..2021-08-31&type=Issues)

## 0.10

### 0.10.2 - 2021-08-25

This is a critical security release, please upgrade to this and see [GHSA-mq5p-2mcr-m52j](https://github.com/jupyterhub/nbgitpuller/security/advisories/GHSA-mq5p-2mcr-m52j) more information.

### 0.10.1 - 2021-06-24

#### Bugs fixed

- Added branch name back to command-line usage [#185](https://github.com/jupyterhub/nbgitpuller/pull/185) ([@sean-morris](https://github.com/sean-morris))

#### Documentation improvements

- Provide cleaner feedback for lint vs test failures [#181](https://github.com/jupyterhub/nbgitpuller/pull/181) ([@yuvipanda](https://github.com/yuvipanda))

#### Continuous integration

- Fix CI failures by disabling pip cache [#188](https://github.com/jupyterhub/nbgitpuller/pull/188) ([@consideRatio](https://github.com/consideRatio))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/nbgitpuller/graphs/contributors?from=2021-06-09&to=2021-06-24&type=c))

[@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3AconsideRatio+updated%3A2021-06-09..2021-06-24&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Amanics+updated%3A2021-06-09..2021-06-24&type=Issues) | [@sean-morris](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Asean-morris+updated%3A2021-06-09..2021-06-24&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Ayuvipanda+updated%3A2021-06-09..2021-06-24&type=Issues)

### 0.10.0 - 2021-06-09

#### Enhancements made

- UI: Branch input placeholder no longer suggests master branch [#180](https://github.com/jupyterhub/nbgitpuller/pull/180) ([@sean-morris](https://github.com/sean-morris))
- Automatically detect default branch name [#179](https://github.com/jupyterhub/nbgitpuller/pull/179) ([@sean-morris](https://github.com/sean-morris))
- Tell users about `main` vs `master` branches [#170](https://github.com/jupyterhub/nbgitpuller/pull/170) ([@yuvipanda](https://github.com/yuvipanda))
- Support generating shiny links [#165](https://github.com/jupyterhub/nbgitpuller/pull/165) ([@yuvipanda](https://github.com/yuvipanda))

#### Bugs fixed

- Handle lack of trailing slashes in hub URLs [#173](https://github.com/jupyterhub/nbgitpuller/pull/173) ([@yuvipanda](https://github.com/yuvipanda))
- Respect path component of JupyterHub url [#172](https://github.com/jupyterhub/nbgitpuller/pull/172) ([@yuvipanda](https://github.com/yuvipanda))
- Parse ssh git URLs properly [#163](https://github.com/jupyterhub/nbgitpuller/pull/163) ([@yuvipanda](https://github.com/yuvipanda))
- Fix failure to restore deleted files (use raw output of git ls-files to avoid quoting unicode) [#156](https://github.com/jupyterhub/nbgitpuller/pull/156) ([@manics](https://github.com/manics))
- Compare current branch to target - don't assume already on target branch locally [#141](https://github.com/jupyterhub/nbgitpuller/pull/141) ([@danlester](https://github.com/danlester))

#### Documentation improvements

- Document restarting notebook process to see changes [#178](https://github.com/jupyterhub/nbgitpuller/pull/178) ([@yuvipanda](https://github.com/yuvipanda))
- docs: update README.md badges [#175](https://github.com/jupyterhub/nbgitpuller/pull/175) ([@consideRatio](https://github.com/consideRatio))
- Add best practices recommendation documentation [#169](https://github.com/jupyterhub/nbgitpuller/pull/169) ([@yuvipanda](https://github.com/yuvipanda))
- Document how to do local development [#162](https://github.com/jupyterhub/nbgitpuller/pull/162) ([@yuvipanda](https://github.com/yuvipanda))
- Add badges to README.md [#150](https://github.com/jupyterhub/nbgitpuller/pull/150) ([@consideRatio](https://github.com/consideRatio))

#### Continuous Integration

- CI: Replace Travis with GitHub workflow [#161](https://github.com/jupyterhub/nbgitpuller/pull/161) ([@manics](https://github.com/manics))
- CI: stop triggering CircleCI on automated pushes to gh-pages [#151](https://github.com/jupyterhub/nbgitpuller/pull/151) ([@consideRatio](https://github.com/consideRatio))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/nbgitpuller/graphs/contributors?from=2020-08-01&to=2021-06-09&type=c))

[@albertmichaelj](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Aalbertmichaelj+updated%3A2020-08-01..2021-06-09&type=Issues) | [@choldgraf](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Acholdgraf+updated%3A2020-08-01..2021-06-09&type=Issues) | [@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3AconsideRatio+updated%3A2020-08-01..2021-06-09&type=Issues) | [@danlester](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Adanlester+updated%3A2020-08-01..2021-06-09&type=Issues) | [@giumas](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Agiumas+updated%3A2020-08-01..2021-06-09&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Amanics+updated%3A2020-08-01..2021-06-09&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Aminrk+updated%3A2020-08-01..2021-06-09&type=Issues) | [@ryanlovett](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Aryanlovett+updated%3A2020-08-01..2021-06-09&type=Issues) | [@SaladRaider](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3ASaladRaider+updated%3A2020-08-01..2021-06-09&type=Issues) | [@samuelmanzer](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Asamuelmanzer+updated%3A2020-08-01..2021-06-09&type=Issues) | [@sean-morris](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Asean-morris+updated%3A2020-08-01..2021-06-09&type=Issues) | [@ttimbers](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Attimbers+updated%3A2020-08-01..2021-06-09&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Awelcome+updated%3A2020-08-01..2021-06-09&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fnbgitpuller+involves%3Ayuvipanda+updated%3A2020-08-01..2021-06-09&type=Issues)

## 0.9

### 0.9.0 - 2020-09-1

- Allow destination to be configured ([#42](https://github.com/jupyterhub/nbgitpuller/pull/42))
- Made the checkout from the reset_deleted_files to use the origin. ([#111](https://github.com/jupyterhub/nbgitpuller/pull/111))
- Update version. ([#112](https://github.com/jupyterhub/nbgitpuller/pull/112))
- Update index.rst ([#113](https://github.com/jupyterhub/nbgitpuller/pull/113))
- Use shallow clones by default ([#117](https://github.com/jupyterhub/nbgitpuller/pull/117))
- updating theme ([#126](https://github.com/jupyterhub/nbgitpuller/pull/126))
- Update ipynb with newer query parameters and toggles ([#127](https://github.com/jupyterhub/nbgitpuller/pull/127))
- Add a mybinder.org tab to the link builder ([#129](https://github.com/jupyterhub/nbgitpuller/pull/129))
- tab activation on link generator ([#132](https://github.com/jupyterhub/nbgitpuller/pull/132))
- fixing bug ([#134](https://github.com/jupyterhub/nbgitpuller/pull/134))
- Fix typo from ipynb link generator external tool reference ([#136](https://github.com/jupyterhub/nbgitpuller/pull/136))
- Use the correct branch for contentRepo ([#138](https://github.com/jupyterhub/nbgitpuller/pull/138))
- Fix file paths or application paths ([#140](https://github.com/jupyterhub/nbgitpuller/pull/140))
- Make the environment repo branch required for binder ([#143](https://github.com/jupyterhub/nbgitpuller/pull/143))
- Travis pypi deployment, README fixes ([#145](https://github.com/jupyterhub/nbgitpuller/pull/145))
- Replace data-8 with jupyterhub ([#146](https://github.com/jupyterhub/nbgitpuller/pull/146))
- CI: fix broken test assertions following --depth 1 by default ([#147](https://github.com/jupyterhub/nbgitpuller/pull/147))
- CI: ensure tox run's flake8 as well ([#148](https://github.com/jupyterhub/nbgitpuller/pull/148))

## 0.8

### 0.8.0 2019-11-23

- Link generator: init application type from query params ([#107](https://github.com/jupyterhub/nbgitpuller/pull/107))
- Made the checkout from the reset_deleted_files to use the origin. ([#111](https://github.com/jupyterhub/nbgitpuller/pull/111))

## 0.7

### 0.7.2 - 2019-10-3

- Bump version number ([#103](https://github.com/jupyterhub/nbgitpuller/pull/103))
- Set authorship info on each commit, rather than repo-wide ([#104](https://github.com/jupyterhub/nbgitpuller/pull/104))
- Bump version number ([#105](https://github.com/jupyterhub/nbgitpuller/pull/105))

### 0.7.1 2019-10-3

- Update version to 0.7.0. ([#100](https://github.com/jupyterhub/nbgitpuller/pull/100))
- Fix legacy links with empty path ([#102](https://github.com/jupyterhub/nbgitpuller/pull/102))
- Bump version number ([#103](https://github.com/jupyterhub/nbgitpuller/pull/103))

### 0.7.0 2019-07-31

- adding a link generator binder ([#49](https://github.com/jupyterhub/nbgitpuller/pull/49))
- Clean up link_generator notebook / app ([#50](https://github.com/jupyterhub/nbgitpuller/pull/50))
- add link to TLJH guide in readme ([#52](https://github.com/jupyterhub/nbgitpuller/pull/52))
- updating link sanitizing ([#54](https://github.com/jupyterhub/nbgitpuller/pull/54))
- adds link to a basic video instruction ([#56](https://github.com/jupyterhub/nbgitpuller/pull/56))
- Add new link generator instructions ([#62](https://github.com/jupyterhub/nbgitpuller/pull/62))
- adding new nbgitpuller link gen app ([#63](https://github.com/jupyterhub/nbgitpuller/pull/63))
- Implement depth/shallow-clone support ([#67](https://github.com/jupyterhub/nbgitpuller/pull/67))
- Made repo_dir an absolute path based on the server_root_dir. ([#71](https://github.com/jupyterhub/nbgitpuller/pull/71))
- Serve gh pages from docs/ not gh-pages ([#73](https://github.com/jupyterhub/nbgitpuller/pull/73))
- Pass nbapp along to GitPuller so it can read from our configuration ([#75](https://github.com/jupyterhub/nbgitpuller/pull/75))
- Rework nbgitpuller link generator ([#76](https://github.com/jupyterhub/nbgitpuller/pull/76))
- Generate URLs that can be launched from canvas ([#78](https://github.com/jupyterhub/nbgitpuller/pull/78))
- Don't require including cloned dir name in path to open ([#79](https://github.com/jupyterhub/nbgitpuller/pull/79))
- adding documentation ([#81](https://github.com/jupyterhub/nbgitpuller/pull/81))
- circle config to push docs ([#82](https://github.com/jupyterhub/nbgitpuller/pull/82))
- documentation clarification ([#88](https://github.com/jupyterhub/nbgitpuller/pull/88))
- Redo documentation ([#92](https://github.com/jupyterhub/nbgitpuller/pull/92))
- Allow git@example.com:repo links ([#97](https://github.com/jupyterhub/nbgitpuller/pull/97))

## 0.6

### 0.6.1 2018-07-19

- Install Jupyter notebook extension by default, Add missing nbgitpuller.json file

### 0.6.0 2018-07-18

- Work with (and require) newer notebook version ([#46](https://github.com/jupyterhub/nbgitpuller/pull/46))
- Update README.md ([#48](https://github.com/jupyterhub/nbgitpuller/pull/48))
