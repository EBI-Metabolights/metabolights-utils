# CHANGELOG


## v1.3.4 (2024-11-20)

### Unknown

* Merge branch 'master' of https://github.com/EBI-Metabolights/metabolights-utils ([`a473347`](https://github.com/EBI-Metabolights/metabolights-utils/commit/a47334735281040c351d47eda681e82ce17b9979))


## v1.3.3 (2024-11-20)

### Fixes

* fix: update search pattern to find new lines in cells ([`bcf703a`](https://github.com/EBI-Metabolights/metabolights-utils/commit/bcf703acad1cbc173e56754aa94dad8742535468))

* fix: ontology source parse errors ([`1d68f25`](https://github.com/EBI-Metabolights/metabolights-utils/commit/1d68f25aa5efc70fda6fa982c3f887b64069b275))


## v1.3.2 (2024-11-20)

### Fixes

* fix: fix isatable read errors ([`dc61316`](https://github.com/EBI-Metabolights/metabolights-utils/commit/dc6131643c48fb21c1ae97994cbef26d58e34e62))

### Unknown

* Merge branch 'master' of https://github.com/EBI-Metabolights/metabolights-utils ([`554f731`](https://github.com/EBI-Metabolights/metabolights-utils/commit/554f731244117c8814171505a5cfb3931dac9be3))


## v1.3.1 (2024-11-14)

### Fixes

* fix: isa table parser fix. ([`af9906c`](https://github.com/EBI-Metabolights/metabolights-utils/commit/af9906c5fc7b22cfa5fd00381c7a98f4fe296ca7))

### Refactoring

* refactor: new local validation endpoint accepts user's api-token ([`4a1c0b8`](https://github.com/EBI-Metabolights/metabolights-utils/commit/4a1c0b8ad25cceae9c48b204648b1f8c5bd24dd0))


## v1.3.0 (2024-11-14)

### Unknown

* Merge branch 'master' of https://github.com/EBI-Metabolights/metabolights-utils ([`94814cf`](https://github.com/EBI-Metabolights/metabolights-utils/commit/94814cf275c6a75d891f146b5235029cc13e9628))


## v1.2.2 (2024-10-23)

### Features

* feat: a new utility method to validate local study with new validation endpoint ([`3db9718`](https://github.com/EBI-Metabolights/metabolights-utils/commit/3db9718af2d90fec6f37476756dbd83a9f4a32d4))

### Fixes

* fix: empty line fix ([`abd88aa`](https://github.com/EBI-Metabolights/metabolights-utils/commit/abd88aa3d3d3562aae3d680e04b9ff3a9ee98a1d))

### Unknown

* Merge branch 'master' of https://github.com/EBI-Metabolights/metabolights-utils ([`ae7fcd4`](https://github.com/EBI-Metabolights/metabolights-utils/commit/ae7fcd4d8e4b18e47f0e25848fcf966e406d9f79))


## v1.2.1 (2024-10-15)

### Fixes

* fix: isa table writer fix ([`e9977ad`](https://github.com/EBI-Metabolights/metabolights-utils/commit/e9977addbe85e27ddc5f521bebf6f002b687f152))

### Unknown

* enable remove_empty_rows and remove_new_lines_in_cells parameters ([`2511db3`](https://github.com/EBI-Metabolights/metabolights-utils/commit/2511db3ddfa402aaaf520e9b946063b44e2fc82a))


## v1.2.0 (2024-10-15)

### Features

* feat: async metabolights study provider implementation ([`5d670b7`](https://github.com/EBI-Metabolights/metabolights-utils/commit/5d670b7a1e8dafe4e0db16199b84e244737236f1))

### Unknown

* async pytest dependency is added ([`ceac7a5`](https://github.com/EBI-Metabolights/metabolights-utils/commit/ceac7a5cc6ead3c6fa1fb49deb193d14aceabb33))


## v1.1.12 (2024-10-14)

### Unknown

* Merge branch 'master' of https://github.com/EBI-Metabolights/metabolights-utils ([`fe54fd8`](https://github.com/EBI-Metabolights/metabolights-utils/commit/fe54fd86a195bc30129b8291cd92560e420bfc9a))


## v1.1.11 (2024-10-12)

### Fixes

* fix: tsv file read improvement ([`46f81a0`](https://github.com/EBI-Metabolights/metabolights-utils/commit/46f81a0c18da2c8f6f79367658a5025852104fe4))

### Refactoring

* refactor: study metadata data model provider is refactored. added a default fix_new_lines_in_cells parameter to  parse isa table file ([`723e757`](https://github.com/EBI-Metabolights/metabolights-utils/commit/723e757f8382c1e3b338776eefb4a575a8502a77))


## v1.1.10 (2024-09-23)

### Testing

* test: test data for new parameter to filter empty isa table rows. ([`9c0cab6`](https://github.com/EBI-Metabolights/metabolights-utils/commit/9c0cab60a6d23acd6b13ee142c63ee95fb22e871))

### Unknown

* Merge branch 'master' of https://github.com/EBI-Metabolights/metabolights-utils ([`78b1e1e`](https://github.com/EBI-Metabolights/metabolights-utils/commit/78b1e1e7b116180bd7abbe131a0dcc245c64417d))


## v1.1.9 (2024-09-18)

### Refactoring

* refactor: new parameter to filter empty isa table rows. ([`d6aa664`](https://github.com/EBI-Metabolights/metabolights-utils/commit/d6aa6644afc4c9bc805df08a633515f135cd4602))

### Unknown

* Merge branch 'master' of https://github.com/EBI-Metabolights/metabolights-utils ([`2c16d3c`](https://github.com/EBI-Metabolights/metabolights-utils/commit/2c16d3c425c53808d2558eadbdee9acb110b739c))


## v1.1.8 (2024-09-13)

### Fixes

* fix: rollback @id field and update investigation tsv file write method ([`ebf17b4`](https://github.com/EBI-Metabolights/metabolights-utils/commit/ebf17b47b70a53d35cc997451ff2ff3b574b9eb8))

* fix: investigation file rows fixed ([`b664483`](https://github.com/EBI-Metabolights/metabolights-utils/commit/b664483025d9d1f938984f916d2c9771e41625d4))

* fix: id field is added to base class ([`ef682f4`](https://github.com/EBI-Metabolights/metabolights-utils/commit/ef682f45b9ec8e5a4c26790c339a1d78c87bace3))

### Refactoring

* refactor: InvestigationFileWriter write method is now aware of inherited classes of Investigation model ([`1928d04`](https://github.com/EBI-Metabolights/metabolights-utils/commit/1928d04ca64cff1a982174b8f61a8d7c96c46658))


## v1.1.7 (2024-09-12)

### Unknown

* Merge branch 'master' of https://github.com/EBI-Metabolights/metabolights-utils ([`600553d`](https://github.com/EBI-Metabolights/metabolights-utils/commit/600553d5c18be24c882b4b0794d05d7fe3302542))


## v1.1.6 (2024-08-30)

### Fixes

* fix: Comment object accepts str ([`88cecca`](https://github.com/EBI-Metabolights/metabolights-utils/commit/88ceccaa56a77cae773f7c74c6b6956ba062abbd))

* fix: validation last update timestamp type is int or float. ([`64c65fa`](https://github.com/EBI-Metabolights/metabolights-utils/commit/64c65faee24fa6b72d0870707d1bce893fb5ac45))

### Unknown

* Merge pull request #2 from nilshoffmann/master

Fixed type of last_update_timestamp in validation to float. ([`fe2aba1`](https://github.com/EBI-Metabolights/metabolights-utils/commit/fe2aba188f7401566bffc72f7f9c2261f8eb93b5))

* Fixed type of last_update_timestamp in validation to float. ([`d1fe8f5`](https://github.com/EBI-Metabolights/metabolights-utils/commit/d1fe8f5f09999f39b85a0cd515f3c717fec6f07f))


## v1.1.5 (2024-07-22)

### Fixes

* fix: dependency updates ([`d0217c1`](https://github.com/EBI-Metabolights/metabolights-utils/commit/d0217c12c3a52991f912f1e156e962540a6d633e))


## v1.1.4 (2024-07-22)

### Fixes

* fix: If there is an undefined characteristics column in sample sheet, set_organism method fails ([`367f919`](https://github.com/EBI-Metabolights/metabolights-utils/commit/367f919ee1731e50283a1e4bedbc26e36488276b))


## v1.1.3 (2024-07-09)

### Fixes

* fix: windows path and new line issues ([`e8cf137`](https://github.com/EBI-Metabolights/metabolights-utils/commit/e8cf1371558ee9d0e29cd142a054359b590b18ee))

### Unknown

* logs in isatab, provider and utils module files, unit test improvements. ([`2d9850a`](https://github.com/EBI-Metabolights/metabolights-utils/commit/2d9850a1031928c01f0c75b590dbd766ba7e4857))


## v1.1.2 (2024-06-23)

### Documentation

* docs: documentation updates and new log messages ([`50055bc`](https://github.com/EBI-Metabolights/metabolights-utils/commit/50055bca6b030f72a2af54c6a6abb9263a89fca3))

### Fixes

* fix: submitted study download error is fixed. ([`ad2cdc8`](https://github.com/EBI-Metabolights/metabolights-utils/commit/ad2cdc883e4bdbed28bc486a16e03a68c6ebb05f))


## v1.1.1 (2024-06-22)

### Fixes

* fix: code updates to fix pylint violations. ([`2a7dae0`](https://github.com/EBI-Metabolights/metabolights-utils/commit/2a7dae02d22a22d39a82a45c685207e11529361a))


## v1.1.0 (2024-06-20)

### Cli

* CLI: submission delete-assay command is added.  After deleting assay file, command downloads the latest metadata files from  MetaboLights study. ([`f6b1ff5`](https://github.com/EBI-Metabolights/metabolights-utils/commit/f6b1ff580bc29484f392e73128d4985fe8ad3037))

### Documentation

* docs: README document and command message updates. ([`1428f25`](https://github.com/EBI-Metabolights/metabolights-utils/commit/1428f25c652ed0bf9fd70e2b7cb284c2d51f3e31))


## v1.0.1 (2024-06-20)

### Continuous Integration

* ci: semantic versioning github actions are enabled. ([`cd7e027`](https://github.com/EBI-Metabolights/metabolights-utils/commit/cd7e0272c743db5c55f5a7ca7e972525a2f2848a))

### Fixes

* fix: public describe and submission describe command fixes. ([`7effb91`](https://github.com/EBI-Metabolights/metabolights-utils/commit/7effb910417575d83d39c30eacd0edc170db7873))


## v1.0.0 (2024-06-20)

### Continuous Integration

* ci: semantic versioning configuration updates ([`085f5f5`](https://github.com/EBI-Metabolights/metabolights-utils/commit/085f5f5778900ccd6e89d66882bd02cca14d8be6))

* ci: github actions to run unit tests ([`3529cd7`](https://github.com/EBI-Metabolights/metabolights-utils/commit/3529cd710eec408e5b266e3e638b91ce5bab84e3))

### Fixes

* fix: python3.8 compatibility, new unit tests and lint fixes. ci: sematic release versioning. ([`3c6bb6f`](https://github.com/EBI-Metabolights/metabolights-utils/commit/3c6bb6f23698551fcb19527ce4d5578c85414f7e))

### Unknown

* feature: Initial commit ([`25c8e5b`](https://github.com/EBI-Metabolights/metabolights-utils/commit/25c8e5b98a3291b137fdbb88113c30263e84ab6c))
