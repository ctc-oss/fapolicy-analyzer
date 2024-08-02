Release notes
===

`fapolicy-analyzer` issues are filed on [GitHub](https://github.com/ctc-oss/fapolicy-analyzer/issues).


## Releases

<!-- towncrier release notes start -->

## [v1.4.0](https://github.com/ctc-oss/fapolicy-analyzer/releases/tag/v1.4.0) - 2024-07-28


### Added

- Added fapolicyd package filter config parser and analyzer. ([#1012](https://github.com/ctc-oss/fapolicy-analyzer/pull/1012))
- Added fapolicyd package filter config editor GUI. ([#1014](https://github.com/ctc-oss/fapolicy-analyzer/pull/1014))

### Fixed

- Address new Py 3.13 eval() parameter list while still supporting RHEL9 Py 3.9 ([#1022](https://github.com/ctc-oss/fapolicy-analyzer/pull/1022))

### Packaging

- Supporting Fedora 41, 40, 39, dropped support for 38. ([#1016](https://github.com/ctc-oss/fapolicy-analyzer/pull/1016))


## [v1.3.0](https://github.com/ctc-oss/fapolicy-analyzer/releases/tag/v1.3.0) - 2024-02-11


### Added

- Allow rules to be loaded dynamically into a profiling session ([#990](https://github.com/ctc-oss/fapolicy-analyzer/pull/990))
- Added syntax highlighting to the fapolicyd config editor ([#991](https://github.com/ctc-oss/fapolicy-analyzer/pull/991))

### Packaging

- Use digest crate for sha256 hashing, removing need for ring crate. ([#984](https://github.com/ctc-oss/fapolicy-analyzer/pull/984))
- Add a version number to the PDF user guide content and filename. ([#995](https://github.com/ctc-oss/fapolicy-analyzer/pull/995))


# v1.2.2

### Added Features

- Revisit pipe operations [[#964](https://github.com/ctc-oss/fapolicy-analyzer/issues/964) [#966](https://github.com/ctc-oss/fapolicy-analyzer/pull/966) @jw3]

### Bug Fixes

- Try harder to back up rules during profiling [[#965](https://github.com/ctc-oss/fapolicy-analyzer/issues/965) [#967](https://github.com/ctc-oss/fapolicy-analyzer/pull/967) @jw3]

### Additional Changes

- Upgrade Pyo3 to 0.20 [[#956](https://github.com/ctc-oss/fapolicy-analyzer/issues/956) [#968](https://github.com/ctc-oss/fapolicy-analyzer/pull/968) @jw3]


# v1.2.1

Packaging updates

Note: RPM artifacts for this release are only available via the Fedora package repositories.

### Bug Fixes

- Failure to build for 32 bit [[#947](https://github.com/ctc-oss/fapolicy-analyzer/issues/947) [#953](https://github.com/ctc-oss/fapolicy-analyzer/pull/953) @jw3]

### Additional Changes

- Remove ExcludeArch from spec [[#948](https://github.com/ctc-oss/fapolicy-analyzer/issues/948) [#953](https://github.com/ctc-oss/fapolicy-analyzer/pull/953) @jw3]
- Upgrade pyo3 [[#882](https://github.com/ctc-oss/fapolicy-analyzer/issues/882) [#905](https://github.com/ctc-oss/fapolicy-analyzer/pull/905) @jw3]
- Bring spec changes back from v1.2 [[#949](https://github.com/ctc-oss/fapolicy-analyzer/issues/949) [#951](https://github.com/ctc-oss/fapolicy-analyzer/pull/951) @jw3]
- Fc not building due to missing crate [[#929](https://github.com/ctc-oss/fapolicy-analyzer/issues/929)]
- Update fc builds [[#946](https://github.com/ctc-oss/fapolicy-analyzer/pull/946) @jw3]

# v1.2.0

### Added Features

- Add GUI support for managing fapolicyd.config [[#830](https://github.com/ctc-oss/fapolicy-analyzer/issues/830) [#909](https://github.com/ctc-oss/fapolicy-analyzer/pull/909) @egbicker]

### Bug Fixes

- Transition away from profiler fails on unsaved changes check [[#940](https://github.com/ctc-oss/fapolicy-analyzer/issues/940) [#941](https://github.com/ctc-oss/fapolicy-analyzer/pull/941) @jw3]
- Text editing state out of sync after deploy [[#934](https://github.com/ctc-oss/fapolicy-analyzer/issues/934) [#935](https://github.com/ctc-oss/fapolicy-analyzer/pull/935) @jw3]
- Erroneous unsaved changes prompts [[#927](https://github.com/ctc-oss/fapolicy-analyzer/issues/927) [#928](https://github.com/ctc-oss/fapolicy-analyzer/pull/928) @egbicker]
- Text editor state issues [[#912](https://github.com/ctc-oss/fapolicy-analyzer/issues/912) [#921](https://github.com/ctc-oss/fapolicy-analyzer/pull/921) @egbicker]
- Config changes from saved sessions do not restore [[#917](https://github.com/ctc-oss/fapolicy-analyzer/issues/917) [#918](https://github.com/ctc-oss/fapolicy-analyzer/pull/918) @jw3]
- Fail to install in fc40 [[#903](https://github.com/ctc-oss/fapolicy-analyzer/issues/903)]

### Additional Changes

- Update config syntax highlighting [[#937](https://github.com/ctc-oss/fapolicy-analyzer/issues/937) [#938](https://github.com/ctc-oss/fapolicy-analyzer/pull/938) @jw3]
- Allow config save override in case of error [[#931](https://github.com/ctc-oss/fapolicy-analyzer/issues/931) [#932](https://github.com/ctc-oss/fapolicy-analyzer/pull/932) @jw3]
- Display config parse errors in GUI [[#925](https://github.com/ctc-oss/fapolicy-analyzer/issues/925) [#926](https://github.com/ctc-oss/fapolicy-analyzer/pull/926) @jw3]
- Fix Gtk version in fapolicyd config file editor UI elements [[#923](https://github.com/ctc-oss/fapolicy-analyzer/issues/923) [#924](https://github.com/ctc-oss/fapolicy-analyzer/pull/924) @tparchambault]
- Change the order of possible issues in start-up initialization failure dlg [[#919](https://github.com/ctc-oss/fapolicy-analyzer/issues/919) [#920](https://github.com/ctc-oss/fapolicy-analyzer/pull/920) @tparchambault]
- Daemon state should not change when loading a user session json file [[#833](https://github.com/ctc-oss/fapolicy-analyzer/issues/833) [#914](https://github.com/ctc-oss/fapolicy-analyzer/pull/914) @tparchambault]
- Deploy config [[#907](https://github.com/ctc-oss/fapolicy-analyzer/issues/907) [#908](https://github.com/ctc-oss/fapolicy-analyzer/pull/908) @jw3]
- xdg environment variables have to be added to /usr/sbin/fapolicy-analyzer [[#454](https://github.com/ctc-oss/fapolicy-analyzer/issues/454)]
- Register config changeset binding class [[#910](https://github.com/ctc-oss/fapolicy-analyzer/pull/910) @jw3]
- Fix bindgen for fc39 [[#915](https://github.com/ctc-oss/fapolicy-analyzer/pull/915) @jw3]
- Add config changes diff [[#913](https://github.com/ctc-oss/fapolicy-analyzer/pull/913) @jw3]
- Format config kv with spaces [[#911](https://github.com/ctc-oss/fapolicy-analyzer/pull/911) @jw3]
- Static load config [[#897](https://github.com/ctc-oss/fapolicy-analyzer/pull/897) @jw3]

**[(Full Changelog)](https://github.com/ctc-oss/fapolicy-analyzer/compare/v1.1.0...v1.2.0)**

# v1.1.0

### Added Features

- Support analysis from libauparse [[#294](https://github.com/ctc-oss/fapolicy-analyzer/issues/294) [#879](https://github.com/ctc-oss/fapolicy-analyzer/pull/879) @jw3]

### Bug Fixes

- Trust parsing broken at fapolicyd 1.3 [[#885](https://github.com/ctc-oss/fapolicy-analyzer/issues/885)]

### Additional Changes

- Testing Rel 1.0.1-1 over FC38. Profiler arg state maintained from prior trial for cleared field [[#850](https://github.com/ctc-oss/fapolicy-analyzer/issues/850) [#856](https://github.com/ctc-oss/fapolicy-analyzer/pull/856) @tparchambault]
- Apt update prior to install in GHA [[#890](https://github.com/ctc-oss/fapolicy-analyzer/pull/890) @jw3]
- Release v1.1.0 [[#888](https://github.com/ctc-oss/fapolicy-analyzer/pull/888) @jw3]
- Move rawhide to fc39 [[#881](https://github.com/ctc-oss/fapolicy-analyzer/pull/881) @jw3]

**[(Full Changelog)](https://github.com/ctc-oss/fapolicy-analyzer/compare/v1.0.3...v1.1.0)**

# v1.0.3

### Added Features

- Support parsing dir keywords [[#588](https://github.com/ctc-oss/fapolicy-analyzer/issues/588) [#872](https://github.com/ctc-oss/fapolicy-analyzer/pull/872) @jw3]
- System upgrade from FC36 to FC38 results in only ~1/3 trusted files [[#866](https://github.com/ctc-oss/fapolicy-analyzer/issues/866)]

### Bug Fixes

- Trust view does not consistently remove deletions [[#736](https://github.com/ctc-oss/fapolicy-analyzer/issues/736)]

### Additional Changes

- Analyzer Time Selection button not working [[#832](https://github.com/ctc-oss/fapolicy-analyzer/issues/832) [#859](https://github.com/ctc-oss/fapolicy-analyzer/pull/859) @egbicker]
- Release v1.0.3 [[#874](https://github.com/ctc-oss/fapolicy-analyzer/pull/874) @jw3]

**[(Full Changelog)](https://github.com/ctc-oss/fapolicy-analyzer/compare/v1.0.2...v1.0.3)**

# v1.0.2

### Added Features

- Enhance the rules deployment confirmation message [[#556](https://github.com/ctc-oss/fapolicy-analyzer/issues/556) [#849](https://github.com/ctc-oss/fapolicy-analyzer/pull/849) @egbicker]
- Lint exe subjects [[#853](https://github.com/ctc-oss/fapolicy-analyzer/issues/853) [#854](https://github.com/ctc-oss/fapolicy-analyzer/pull/854) @jw3]

### Bug Fixes

- Service active check [[#860](https://github.com/ctc-oss/fapolicy-analyzer/issues/860) [#861](https://github.com/ctc-oss/fapolicy-analyzer/pull/861) @jw3]
- Ancillary Trust not reloaded after deployment rollback [[#827](https://github.com/ctc-oss/fapolicy-analyzer/issues/827) [#840](https://github.com/ctc-oss/fapolicy-analyzer/pull/840) @dorschs57]
- Ancillary Trust not reloading properly after opening session file [[#828](https://github.com/ctc-oss/fapolicy-analyzer/issues/828) [#840](https://github.com/ctc-oss/fapolicy-analyzer/pull/840) @dorschs57]
- Service valid check is not accurate [[#851](https://github.com/ctc-oss/fapolicy-analyzer/issues/851) [#852](https://github.com/ctc-oss/fapolicy-analyzer/pull/852) @jw3]

### Additional Changes

- Rust rules_difference function not handling edits and additions correctly [[#847](https://github.com/ctc-oss/fapolicy-analyzer/issues/847)]
- Release v1.0.2 [[#862](https://github.com/ctc-oss/fapolicy-analyzer/pull/862) @jw3]

**[(Full Changelog)](https://github.com/ctc-oss/fapolicy-analyzer/compare/v1.0.1...v1.0.2)**

# v1.0.1

### Added Features

- Release User Guide PDF [[#841](https://github.com/ctc-oss/fapolicy-analyzer/pull/841) @jw3]
- Trust file count should indicate displayed of total [[#803](https://github.com/ctc-oss/fapolicy-analyzer/issues/803) [#839](https://github.com/ctc-oss/fapolicy-analyzer/pull/839) @egbicker]

### Bug Fixes

- Rules parse message: Expected one of .. [[#802](https://github.com/ctc-oss/fapolicy-analyzer/issues/802) [#845](https://github.com/ctc-oss/fapolicy-analyzer/pull/845) @jw3]
- Profiler Target information is being lost after navigation [[#818](https://github.com/ctc-oss/fapolicy-analyzer/issues/818) [#820](https://github.com/ctc-oss/fapolicy-analyzer/pull/820) @jw3]
- Analyzer Go to Rule context menu not working from Profiler [[#831](https://github.com/ctc-oss/fapolicy-analyzer/issues/831) [#837](https://github.com/ctc-oss/fapolicy-analyzer/pull/837) @egbicker]

### Additional Changes

- Bump versions for v1.1.0 [[#835](https://github.com/ctc-oss/fapolicy-analyzer/pull/835) @jw3]

**[(Full Changelog)](https://github.com/ctc-oss/fapolicy-analyzer/compare/v1.0.0...v1.0.1)**

# v1.0.0

Initial release
