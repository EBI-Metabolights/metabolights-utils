# CHANGELOG


## v1.4.14 (2025-11-25)

### Fix

- isa-tab performer and date colum patterns are defined. local validation improvements.

## v1.4.13 (2025-11-24)

### Fix

- local validate command is added

## v1.4.12 (2025-11-18)

### Fix

- add created_at field in studyDbMetadata

## v1.4.11 (2025-11-04)

### Fix

- folder metadata collector error

## v1.4.10 (2025-11-04)

### Refactor

- enable to load study folder metadata (for metadata files and data files) from different folders.

## v1.4.9 (2025-10-05)

### Fix

- get study schema does not get version parameter.

## v1.4.8 (2025-09-29)

### Fix

- study model version is updated.

## v1.4.7 (2025-09-29)

### Fix

- assay result file format and study template version fields are added.

## v1.4.6 (2025-09-27)

### Fix

- model update with new fields and lint fixes
- investigation file comment handling. Fix lint errors.

## v1.4.5 (2025-09-26)

### Fix

- documentation update

## v1.4.4 (2025-06-27)

### Bug Fixes

- Isa table file save without hash check
  ([`728bd61`](https://github.com/EBI-Metabolights/metabolights-utils/commit/728bd6115eec146ab393f61fa7296ccff8141d23))


## v1.4.3 (2025-04-02)

### Bug Fixes

- Write investigation file
  ([`3f89da6`](https://github.com/EBI-Metabolights/metabolights-utils/commit/3f89da62d56fc97319add1aea6b8ba27cc116ea5))


## v1.4.2 (2025-02-15)


## v1.4.1 (2025-02-11)

### Refactoring

- Provisional and private study status are accepted. They will converted to submitted and in
  curation status respectively.
  ([`8372ca9`](https://github.com/EBI-Metabolights/metabolights-utils/commit/8372ca9f53f80f880e2a7127f89700556d26b35c))


## v1.4.0 (2025-02-11)

### Bug Fixes

- Data folder size calculation errors.
  ([`36f61f9`](https://github.com/EBI-Metabolights/metabolights-utils/commit/36f61f90f74c6596a3b0a312db7e7254c7b27fd5))


## v1.3.12 (2025-01-19)

### Features

- New command to create metabolights study model on local (mtbls model create)
  ([`9415dc8`](https://github.com/EBI-Metabolights/metabolights-utils/commit/9415dc839ca33edfefc233fc36109f8083cf1c97))


## v1.3.11 (2025-01-19)

### Bug Fixes

- Python version support
  ([`4bf7be2`](https://github.com/EBI-Metabolights/metabolights-utils/commit/4bf7be24ecbaf93c19c23418dbda9042248e7895))

- Tsv file read fix and lint updates
  ([`e95246d`](https://github.com/EBI-Metabolights/metabolights-utils/commit/e95246dfbcaa2769753a29f3ff02bbbb91b50099))

### Documentation

- Initial docs folder
  ([`38e286f`](https://github.com/EBI-Metabolights/metabolights-utils/commit/38e286f35f847ad74bd11cab037bb8e6bca20f85))

### Refactoring

- Ruff lint fixes
  ([`4f4d601`](https://github.com/EBI-Metabolights/metabolights-utils/commit/4f4d601da90534f0ddbaa142ef79c0d92f5ad7e4))

- Ruff lint fixes
  ([`7be0b4e`](https://github.com/EBI-Metabolights/metabolights-utils/commit/7be0b4e062be57be5cb27f0fc7c87704e64cfd84))


## v1.3.10 (2024-12-19)


## v1.3.9 (2024-12-06)

### Bug Fixes

- Investigation file parse error and ruff is used for formatting and linting.
  ([`1918ee6`](https://github.com/EBI-Metabolights/metabolights-utils/commit/1918ee69e261e2a5495c97b612bacd2c89a88259))


## v1.3.8 (2024-12-06)

### Refactoring

- Column add method is defined.
  ([`428b7ff`](https://github.com/EBI-Metabolights/metabolights-utils/commit/428b7ffae6363298475cb02e8d00009840ceedb8))

- File formats are updated with isort and black.
  ([`187b100`](https://github.com/EBI-Metabolights/metabolights-utils/commit/187b1004332e3fae5fcce3c01a05c3b64b561d83))

- Refactor code to export modules
  ([`cadbafd`](https://github.com/EBI-Metabolights/metabolights-utils/commit/cadbafdb1fea5f95556a04f1855af287bb2935c0))


## v1.3.7 (2024-12-01)

### Bug Fixes

- Get_study_metadata_path method update
  ([`75d221c`](https://github.com/EBI-Metabolights/metabolights-utils/commit/75d221cd45124f441381c9ff67ae33e2e0621807))


## v1.3.6 (2024-11-26)


## v1.3.5 (2024-11-21)

### Bug Fixes

- Strip qoutation characters while reading ISA table file
  ([`b6aa029`](https://github.com/EBI-Metabolights/metabolights-utils/commit/b6aa0297a1d68b22004ca92c37c40f4b07ebc994))


## v1.3.4 (2024-11-20)

### Refactoring

- Upload submission refactor and create study utility method
  ([`c9ea043`](https://github.com/EBI-Metabolights/metabolights-utils/commit/c9ea043919834d00610d34e8dbe39ea00b8dba53))


## v1.3.3 (2024-11-20)

### Bug Fixes

- Ontology source parse errors
  ([`1d68f25`](https://github.com/EBI-Metabolights/metabolights-utils/commit/1d68f25aa5efc70fda6fa982c3f887b64069b275))

- Update search pattern to find new lines in cells
  ([`bcf703a`](https://github.com/EBI-Metabolights/metabolights-utils/commit/bcf703acad1cbc173e56754aa94dad8742535468))


## v1.3.2 (2024-11-20)

### Bug Fixes

- Fix isatable read errors
  ([`dc61316`](https://github.com/EBI-Metabolights/metabolights-utils/commit/dc6131643c48fb21c1ae97994cbef26d58e34e62))


## v1.3.1 (2024-11-14)

### Bug Fixes

- Isa table parser fix.
  ([`af9906c`](https://github.com/EBI-Metabolights/metabolights-utils/commit/af9906c5fc7b22cfa5fd00381c7a98f4fe296ca7))

### Refactoring

- New local validation endpoint accepts user's api-token
  ([`4a1c0b8`](https://github.com/EBI-Metabolights/metabolights-utils/commit/4a1c0b8ad25cceae9c48b204648b1f8c5bd24dd0))


## v1.3.0 (2024-11-14)


## v1.2.2 (2024-10-23)

### Bug Fixes

- Empty line fix
  ([`abd88aa`](https://github.com/EBI-Metabolights/metabolights-utils/commit/abd88aa3d3d3562aae3d680e04b9ff3a9ee98a1d))

### Features

- A new utility method to validate local study with new validation endpoint
  ([`3db9718`](https://github.com/EBI-Metabolights/metabolights-utils/commit/3db9718af2d90fec6f37476756dbd83a9f4a32d4))


## v1.2.1 (2024-10-15)

### Bug Fixes

- Isa table writer fix
  ([`e9977ad`](https://github.com/EBI-Metabolights/metabolights-utils/commit/e9977addbe85e27ddc5f521bebf6f002b687f152))


## v1.2.0 (2024-10-15)

### Features

- Async metabolights study provider implementation
  ([`5d670b7`](https://github.com/EBI-Metabolights/metabolights-utils/commit/5d670b7a1e8dafe4e0db16199b84e244737236f1))


## v1.1.12 (2024-10-14)


## v1.1.11 (2024-10-12)

### Bug Fixes

- Tsv file read improvement
  ([`46f81a0`](https://github.com/EBI-Metabolights/metabolights-utils/commit/46f81a0c18da2c8f6f79367658a5025852104fe4))

### Refactoring

- Study metadata data model provider is refactored. added a default fix_new_lines_in_cells parameter
  to parse isa table file
  ([`723e757`](https://github.com/EBI-Metabolights/metabolights-utils/commit/723e757f8382c1e3b338776eefb4a575a8502a77))


## v1.1.10 (2024-09-23)

### Testing

- Test data for new parameter to filter empty isa table rows.
  ([`9c0cab6`](https://github.com/EBI-Metabolights/metabolights-utils/commit/9c0cab60a6d23acd6b13ee142c63ee95fb22e871))


## v1.1.9 (2024-09-18)

### Refactoring

- New parameter to filter empty isa table rows.
  ([`d6aa664`](https://github.com/EBI-Metabolights/metabolights-utils/commit/d6aa6644afc4c9bc805df08a633515f135cd4602))


## v1.1.8 (2024-09-13)

### Bug Fixes

- Id field is added to base class
  ([`ef682f4`](https://github.com/EBI-Metabolights/metabolights-utils/commit/ef682f45b9ec8e5a4c26790c339a1d78c87bace3))

- Investigation file rows fixed
  ([`b664483`](https://github.com/EBI-Metabolights/metabolights-utils/commit/b664483025d9d1f938984f916d2c9771e41625d4))

- Rollback @id field and update investigation tsv file write method
  ([`ebf17b4`](https://github.com/EBI-Metabolights/metabolights-utils/commit/ebf17b47b70a53d35cc997451ff2ff3b574b9eb8))

### Refactoring

- Investigationfilewriter write method is now aware of inherited classes of Investigation model
  ([`1928d04`](https://github.com/EBI-Metabolights/metabolights-utils/commit/1928d04ca64cff1a982174b8f61a8d7c96c46658))


## v1.1.7 (2024-09-12)


## v1.1.6 (2024-08-30)

### Bug Fixes

- Comment object accepts str
  ([`88cecca`](https://github.com/EBI-Metabolights/metabolights-utils/commit/88ceccaa56a77cae773f7c74c6b6956ba062abbd))

- Validation last update timestamp type is int or float.
  ([`64c65fa`](https://github.com/EBI-Metabolights/metabolights-utils/commit/64c65faee24fa6b72d0870707d1bce893fb5ac45))


## v1.1.5 (2024-07-22)

### Bug Fixes

- Dependency updates
  ([`d0217c1`](https://github.com/EBI-Metabolights/metabolights-utils/commit/d0217c12c3a52991f912f1e156e962540a6d633e))


## v1.1.4 (2024-07-22)

### Bug Fixes

- If there is an undefined characteristics column in sample sheet, set_organism method fails
  ([`367f919`](https://github.com/EBI-Metabolights/metabolights-utils/commit/367f919ee1731e50283a1e4bedbc26e36488276b))


## v1.1.3 (2024-07-09)

### Bug Fixes

- Windows path and new line issues
  ([`e8cf137`](https://github.com/EBI-Metabolights/metabolights-utils/commit/e8cf1371558ee9d0e29cd142a054359b590b18ee))


## v1.1.2 (2024-06-23)

### Bug Fixes

- Submitted study download error is fixed.
  ([`ad2cdc8`](https://github.com/EBI-Metabolights/metabolights-utils/commit/ad2cdc883e4bdbed28bc486a16e03a68c6ebb05f))

### Documentation

- Documentation updates and new log messages
  ([`50055bc`](https://github.com/EBI-Metabolights/metabolights-utils/commit/50055bca6b030f72a2af54c6a6abb9263a89fca3))


## v1.1.1 (2024-06-22)

### Bug Fixes

- Code updates to fix pylint violations.
  ([`2a7dae0`](https://github.com/EBI-Metabolights/metabolights-utils/commit/2a7dae02d22a22d39a82a45c685207e11529361a))


## v1.1.0 (2024-06-20)

### Documentation

- Readme document and command message updates.
  ([`1428f25`](https://github.com/EBI-Metabolights/metabolights-utils/commit/1428f25c652ed0bf9fd70e2b7cb284c2d51f3e31))


## v1.0.1 (2024-06-20)

### Bug Fixes

- Public describe and submission describe command fixes.
  ([`7effb91`](https://github.com/EBI-Metabolights/metabolights-utils/commit/7effb910417575d83d39c30eacd0edc170db7873))

### Continuous Integration

- Semantic versioning github actions are enabled.
  ([`cd7e027`](https://github.com/EBI-Metabolights/metabolights-utils/commit/cd7e0272c743db5c55f5a7ca7e972525a2f2848a))


## v1.0.0 (2024-06-20)

### Bug Fixes

- Python3.8 compatibility, new unit tests and lint fixes. ci: sematic release versioning.
  ([`3c6bb6f`](https://github.com/EBI-Metabolights/metabolights-utils/commit/3c6bb6f23698551fcb19527ce4d5578c85414f7e))

### Continuous Integration

- Github actions to run unit tests
  ([`3529cd7`](https://github.com/EBI-Metabolights/metabolights-utils/commit/3529cd710eec408e5b266e3e638b91ce5bab84e3))

- Semantic versioning configuration updates
  ([`085f5f5`](https://github.com/EBI-Metabolights/metabolights-utils/commit/085f5f5778900ccd6e89d66882bd02cca14d8be6))
