# CHANGELOG

## v1.1.0 (2025-07-27)

### Bug Fixes
* Admit none in Queryset schema returning an empty queryset [`e686884`](https://github.com/bnznamco/django-structured-field/commit/e686884)

* Fix args order preservation in recursive annotation list [`cebbdbe`](https://github.com/bnznamco/django-structured-field/commit/cebbdbe)

* Fix future annotation evaluation in patch_annotation [`690a6e1`](https://github.com/bnznamco/django-structured-field/commit/690a6e1)

### Chores
* Drop support for python 3.8 [`49bd5d3`](https://github.com/bnznamco/django-structured-field/commit/49bd5d3)

### Features
* Added possibility to specify a custom serliazer for ForeignKey and QuerySet fields [`4605dd6`](https://github.com/bnznamco/django-structured-field/commit/4605dd6)

## v1.0.0 (2025-07-23)

### Bug Fixes
* Ignore data merging for lists in DRF PATCH ([`#3`](https://github.com/bnznamco/django-structured-field/pull/3), [`17311fb`](https://github.com/bnznamco/django-structured-field/commit/17311fb))

### Chores
* Update semantic release to v10 ([`25e369b`](https://github.com/bnznamco/django-structured-field/commit/25e369b))

## v0.5.1 (2025-06-27)

### Documentation

* docs: update changelog ([`13bb8e4`](https://github.com/bnznamco/django-structured-field/commit/13bb8e44d5ccc53c89d0fe6b2ae1f71a4fcb3c12))

* docs: update migrate data documentation ([`5619d14`](https://github.com/bnznamco/django-structured-field/commit/5619d14e23c4796700376bc1db965c035b47f71b))

### Fix

* fix: correctly resolve complete url in filefields inside structured relations ([`fbb6424`](https://github.com/bnznamco/django-structured-field/commit/fbb6424f764a9d35ff8d68571cd54711e2364a48))

### Unknown

* tests: add test to ensure correct absolute url building for filefields ([`6d384c6`](https://github.com/bnznamco/django-structured-field/commit/6d384c621bc906fdc1aaba91493578de7bafca55))


## v0.5.0 (2025-05-30)

### Chore

* chore: update test app migrations ([`ec06577`](https://github.com/bnznamco/django-structured-field/commit/ec06577a363512fb2e9d94ea18732101f3ce0868))

* chore: increase logging level in test app ([`77ec645`](https://github.com/bnznamco/django-structured-field/commit/77ec6452ab2fac76592c941daea587ef78e1c42e))

* chore: added some logging to the admin widget to better debug admin panel errors ([`d5d5067`](https://github.com/bnznamco/django-structured-field/commit/d5d50675d831b2a9281714de302431e5355b7979))

* chore: added some debug logging in pydantic model patching to debug better the process of field patching ([`96f57c0`](https://github.com/bnznamco/django-structured-field/commit/96f57c02511720b338ef23ab76ca6b28befc7673))

### Documentation

* docs: added documentation of data migration ([`498a910`](https://github.com/bnznamco/django-structured-field/commit/498a910954f91d1d70a134ea45a10670481def98))

### Feature

* feat(migrations): added command to generate database migrations for structured fields ([`cd29144`](https://github.com/bnznamco/django-structured-field/commit/cd2914468cd9637db0f89bd55fe0514aa5652456))

* feat(core): added `ConfigDict(extra=&#39;ignore&#39;)` to ignore extra keys from validation. This helps with db validation issues when removing keys. ([`eda841f`](https://github.com/bnznamco/django-structured-field/commit/eda841fd12faa360a25ef288021d86ba38043840))

### Fix

* fix: model validation when model is actually already validated ([`0b0f4da`](https://github.com/bnznamco/django-structured-field/commit/0b0f4da78c4dcd594d56eb6360fb1887135110c9))

* fix(field): fix DB save with direct python dict reference, casting to model during value preparation ([`91ec4ef`](https://github.com/bnznamco/django-structured-field/commit/91ec4efe618865dd604172656634ab46309112f7))

* fix(literals): fix literals future annotations ([`732a7fe`](https://github.com/bnznamco/django-structured-field/commit/732a7fe7ac0a8a6f3e4203c790286db420954c0d))

### Unknown

* tests: removed unused typing imports ([`180b444`](https://github.com/bnznamco/django-structured-field/commit/180b4442fe25b8bdcff37a0143c7e41f3526b1a5))

* Merge branch &#39;master&#39; into feature/dbvalidation ([`9b9befe`](https://github.com/bnznamco/django-structured-field/commit/9b9befeb9bd8070ab8de49477c054ed479f7f7d5))

* tests: added Union of Models with field discriminator in testcases ([`f1e94bf`](https://github.com/bnznamco/django-structured-field/commit/f1e94bfeef6da7db72eef878bd286349f0d3bf9f))


## v0.4.3 (2025-05-27)

### Fix

* fix(drf): fix drf serialization for Fk and Qs fields ([`4199fc7`](https://github.com/bnznamco/django-structured-field/commit/4199fc74f1b394838983153e7be7f188196837e7))

### Refactor

* refactor: separate qs and fk fields ([`9f3380e`](https://github.com/bnznamco/django-structured-field/commit/9f3380e815ac8dace686d030b992d52806cf6821))


## v0.4.2 (2025-05-23)

### Chore

* chore: drop support for django 3.2 ([`7a3bb81`](https://github.com/bnznamco/django-structured-field/commit/7a3bb81e668592e885fb97423dc936f131f1bb05))

* chore: drop support for django 3.2 ([`bf080d2`](https://github.com/bnznamco/django-structured-field/commit/bf080d262c14709a1be238e7ce0cafe28c033309))

* chore: updated logo ([`91d1b58`](https://github.com/bnznamco/django-structured-field/commit/91d1b5832b16804ab4d1ae3fff7b7d30fce79e97))

### Documentation

* docs: remove edit links ([`91b1cba`](https://github.com/bnznamco/django-structured-field/commit/91b1cbae5d26ceb28baf1526956d409fdc20a8bd))

* docs: fix home button hover style ([`fd27d50`](https://github.com/bnznamco/django-structured-field/commit/fd27d505ce7f9a0e047b1655773bf0a9a0777b75))

* docs: update contents ([`695f3a5`](https://github.com/bnznamco/django-structured-field/commit/695f3a53d7ba8180183e8cb2e0cabcd2ffbd0893))

* docs: update changelog ([`21b7249`](https://github.com/bnznamco/django-structured-field/commit/21b72492faf4fc492e141d2d8c81ac7ad7a92f78))

* docs: switch to static sidebar to better organize content ([`be525d7`](https://github.com/bnznamco/django-structured-field/commit/be525d755445632f12ff690edfb3b075b2be8c4f))

* docs: updated to vuepress 2 ([`a03b155`](https://github.com/bnznamco/django-structured-field/commit/a03b155355b11640e5a70a3df3068c393c90f6b1))

* docs: added github-pages docs ([`853b759`](https://github.com/bnznamco/django-structured-field/commit/853b7590c1e47d887ae5c09c54d82094e5b20d66))

### Fix

* fix: fix pydantic &gt;= 2.10 compatibility ([`89d5a36`](https://github.com/bnznamco/django-structured-field/commit/89d5a3671c08b6dfa776044af1601c4ea7e1d6e0))

* fix: fix queryset field requiring &#39;name&#39; and &#39;model&#39; fields in dict validation ([`ede98d5`](https://github.com/bnznamco/django-structured-field/commit/ede98d5ffad5cec17f54df095c54037760e47260))

* fix(foreignkey): fix foreignkey serialize_data abstract model serializer class discovery ([`a15d33e`](https://github.com/bnznamco/django-structured-field/commit/a15d33ea0653f8c58c71dfe5272e0040c4b4af96))

### Unknown

* feature: handle partial updates during django rest framework PATCH request ([`57e778b`](https://github.com/bnznamco/django-structured-field/commit/57e778b13cead8595a3af94184f0d78fe4cf4eaa))

* tests: update queryset tests to check more validations cases ([`04359fd`](https://github.com/bnznamco/django-structured-field/commit/04359fd8b24d1ee6dbacdafdcf04af3eef9768d9))


## v0.4.1 (2025-02-03)

### Fix

* fix: added structured/contrib in MANIFEST ([`2a20044`](https://github.com/bnznamco/django-structured-field/commit/2a20044a8ce93d01a97b86b6acaf24a4447b2196))


## v0.4.0 (2024-11-26)

### Chore

* chore: update python compatibility ([`d091026`](https://github.com/bnznamco/django-structured-field/commit/d0910268c4de94ac658101c28af95bbafc4d78e1))

* chore: update rollup build to output minified code ([`69127b9`](https://github.com/bnznamco/django-structured-field/commit/69127b92441030db24279bf88c7de102db10eb7b))

* chore: update README codecov badge ⛱ ([`cdc8dd2`](https://github.com/bnznamco/django-structured-field/commit/cdc8dd2ab1dfc1921c2f7850a98ebd93b315de24))

* chore: update github CI ([`5391215`](https://github.com/bnznamco/django-structured-field/commit/539121565ab3585f00c1f3398f48b4f108d8317e))

* chore: add compatibility for django 5.1 ([`2ce7d69`](https://github.com/bnznamco/django-structured-field/commit/2ce7d695f3fdff9addfacbcba05ea46e97e4e22e))

### Feature

* feat(core): added `{field.attname}_raw` for StructuredJSONField raw data inspection to instance class ([`0c34c65`](https://github.com/bnznamco/django-structured-field/commit/0c34c65cff619c42ea4881a7bb2b8a838358a763))

### Fix

* fix: fix compatibility with python 3.8 ([`1466f02`](https://github.com/bnznamco/django-structured-field/commit/1466f021be866492061d685233ea27b73a540929))

### Refactor

* refactor: move raw field generation to contribute_to_class ([`ef93706`](https://github.com/bnznamco/django-structured-field/commit/ef937061e9a36bc800451434de981da5c7620a53))

* refactor: refactor utils code ([`af6e75d`](https://github.com/bnznamco/django-structured-field/commit/af6e75d18a1ae926b8597e36ea904ab2891cc60f))

* refactor: cache engine code refactor ([`0774e7d`](https://github.com/bnznamco/django-structured-field/commit/0774e7d09d188bd96daeccef87b6e920652bdade))


## v0.3.1 (2024-11-18)

### Fix

* fix(cache): added signals to update cache entries in shared cache ([`333e422`](https://github.com/bnznamco/django-structured-field/commit/333e42243054942d39378b20738a6ad01bf12b74))

### Unknown

* tests: update test models ([`8c6ca2a`](https://github.com/bnznamco/django-structured-field/commit/8c6ca2a29e3cbcef0115c35ee3e84c6044c506e3))

* deps: update to pydantic 2.9.2 ([`ba21a56`](https://github.com/bnznamco/django-structured-field/commit/ba21a562efd67f29013d4385d92b0b7ca68019df))

* tests: update cache tests ([`f9a763a`](https://github.com/bnznamco/django-structured-field/commit/f9a763a9b418794aae448294889972cc60e34b6d))


## v0.3.0 (2024-11-17)

### Feature

* feat(admin): autopopolate items in admin search with paginated responses ([`fe15ee0`](https://github.com/bnznamco/django-structured-field/commit/fe15ee07a22306d3617774f0cf944cfbe936622e))

### Fix

* fix(pydantic): fix serializations of Qs field ([`995e5e1`](https://github.com/bnznamco/django-structured-field/commit/995e5e1d5331984a5f11ec80d78cf1358d33d9c5))

* fix(pydantic): fix pydantic annotation inspection ([`2c17531`](https://github.com/bnznamco/django-structured-field/commit/2c17531678939b1fd28f8c7c049cc0f46feab55a))

* fix(abstract): fix compatibility with abstract foreign key ([`46b12e4`](https://github.com/bnznamco/django-structured-field/commit/46b12e4104aabe1dc216ee082c1468d0ed005334))

### Refactor

* refactor(pydantic): refactor annotation patching logic, now handling recustions ([`d5aa257`](https://github.com/bnznamco/django-structured-field/commit/d5aa257f0f82830ff2cf192f26c596b9524ff757))

### Unknown

* tests: fix tests for shared cache ([`f080e10`](https://github.com/bnznamco/django-structured-field/commit/f080e10368220959f6ac0edd59d1301a13954f2b))

* tests: run tests both with cache on and off and shared cache ([`8af9203`](https://github.com/bnznamco/django-structured-field/commit/8af92032677dd7731dcebc48f12e3476e2efeff4))

* tests: run tests both with cache on and off ([`76fb3ec`](https://github.com/bnznamco/django-structured-field/commit/76fb3ec8f391423a18aa71c1ee1804ac24d1d5a1))

* tests: update tests for abstract querysets ([`f544ce6`](https://github.com/bnznamco/django-structured-field/commit/f544ce62b31e7f4373d066b1900e9427152a2d9d))


## v0.2.1 (2024-11-15)

### Fix

* fix(admin): fix m2m empty value ([`99c0404`](https://github.com/bnznamco/django-structured-field/commit/99c04046c0913cac341c46548c651129bae9c471))


## v0.2.0 (2024-10-26)

### Chore

* chore: update ci testing codecov upload ([`593947d`](https://github.com/bnznamco/django-structured-field/commit/593947dbbf3df86770b59cf8f6db7bd5f70ef303))

### Documentation

* docs: update readme admin and restframework integrations ([`d4f84d8`](https://github.com/bnznamco/django-structured-field/commit/d4f84d82301dad3affe5e6e10ca07b7b93f0d2f0))

* docs: update readme shields ([`68f363a`](https://github.com/bnznamco/django-structured-field/commit/68f363aae9f5ac7e23f0197baaf7c38263db1b7f))

### Feature

* feat(admin): added compatibility for Queryset field in admin ([`5cc6aa2`](https://github.com/bnznamco/django-structured-field/commit/5cc6aa2ddf59010a25c7f5116cb9bcbcbe769456))

* feat(admin): make relations nullable in json-form schema ([`3763192`](https://github.com/bnznamco/django-structured-field/commit/376319254ad00f9e03e9b403c0adc202ba6c600a))

* feat(core): added compatibility with abstract model relations ([`8e0d6c1`](https://github.com/bnznamco/django-structured-field/commit/8e0d6c1f6efaf3a979642b63fee59ae369e97a62))

* feat(admin): better search capabilities for admin panel ([`a782592`](https://github.com/bnznamco/django-structured-field/commit/a782592eb19dd39c600c9021f96c00e478fc3b7a))

### Fix

* fix(admin): fix widget wrong method alias &#39;model_json_schema&#39; ([`028dae9`](https://github.com/bnznamco/django-structured-field/commit/028dae94282b0492d8221f5b978d87b63efd9d30))

* fix(field): fix structured field typing annotations import ([`de088ac`](https://github.com/bnznamco/django-structured-field/commit/de088ac02a4dac5bae7dd462f09bdb5abdb75634))

### Refactor

* refactor(admin): remove unused js ([`86b5a38`](https://github.com/bnznamco/django-structured-field/commit/86b5a38ce86bd3b5d78ec1b34a7549211fd5c66b))

### Unknown

* deps(jsoneditor): update jsoneditor version ([`8ecf724`](https://github.com/bnznamco/django-structured-field/commit/8ecf724e603072b274a7eaa2a06e7020407472ae))


## v0.1.0 (2024-07-12)

### Chore

* chore: limit compatibility to python &gt;= 3.9 ([`b7754ad`](https://github.com/bnznamco/django-structured-field/commit/b7754ada06443517846b1a185ccd8a9e4470cc1b))

* chore: better typing suggestions for cache enabled models ([`0cb660e`](https://github.com/bnznamco/django-structured-field/commit/0cb660e814c9ab95c8235344797fcf9f1accb3ba))

* chore: fix typing error on ci tests ([`d3be04e`](https://github.com/bnznamco/django-structured-field/commit/d3be04e3c849ca27822f904ace2defec76a8b97c))

* chore: fir typo in requirements.txt ([`62a56df`](https://github.com/bnznamco/django-structured-field/commit/62a56df244486aeb74c59390edb9c2f0f7130ee8))

* chore: update ci testing versions ([`0d2cae1`](https://github.com/bnznamco/django-structured-field/commit/0d2cae16adfc2536a3df23670d7e90c039df62f2))

* chore: update ci testing versions ([`e35f276`](https://github.com/bnznamco/django-structured-field/commit/e35f276f13246bb0c30510e6f14f49f63849c454))

* chore: fix rollup watching ([`43f016c`](https://github.com/bnznamco/django-structured-field/commit/43f016c7899c55ddd59ab49f5f9a9c9d3cc69804))

* chore: change js form placeholder for qs ([`4ca997d`](https://github.com/bnznamco/django-structured-field/commit/4ca997d5c0bc4cfbb4ce5b296cc400f59080a9af))

* chore: remove structured model form ([`78fdcf2`](https://github.com/bnznamco/django-structured-field/commit/78fdcf241e61b7eb63501053519fa1d60abc4cd3))

* chore: added jsoneditor.js.map ([`cdaa86d`](https://github.com/bnznamco/django-structured-field/commit/cdaa86d847bf8e732d6fa3f678ab066aec4039ab))

* chore: first commit 🙀 ([`9a29807`](https://github.com/bnznamco/django-structured-field/commit/9a2980781c45b9b075f9451207221219356e9572))

### Documentation

* docs: update readme settings section 🐸 ([`1d2d5bd`](https://github.com/bnznamco/django-structured-field/commit/1d2d5bddc304561c7a6d245690e1650c3b73a20c))

* docs: update readme 🐸 ([`8afe82b`](https://github.com/bnznamco/django-structured-field/commit/8afe82b27763dd3efd65f707b9c9ded653dba30f))

* docs: update README 📒 ([`f2dc816`](https://github.com/bnznamco/django-structured-field/commit/f2dc8164d95d4598597fa2e8842002ba40a86119))

* docs: update README 📒 ([`933ebb5`](https://github.com/bnznamco/django-structured-field/commit/933ebb504956e80653a806a016f64012af6bdc5a))

### Feature

* feat: added settings to enable shared cache experimental features ([`535ada5`](https://github.com/bnznamco/django-structured-field/commit/535ada5fbf301b2084957c71b82d6dba795b790f))

* feat: first draft for a shared cache between instances and fields ([`5862559`](https://github.com/bnznamco/django-structured-field/commit/58625597e8cfe82bd4c3ea7c61656c42220d981d))

* feat: better visibility for autocomplete selected item in multiple relations ([`20f6497`](https://github.com/bnznamco/django-structured-field/commit/20f649757fc6e18813a784fe3af4d16bbe7a27b9))

* feat: better visibility to selected option in m2m fields editor ([`7b16dae`](https://github.com/bnznamco/django-structured-field/commit/7b16dae4f92c7a34daa13706650b5e7f74ed2e31))

* feat: adapt dark schema css ([`11621ca`](https://github.com/bnznamco/django-structured-field/commit/11621ca460c72ed2009c4611ea431f5ab73dce6b))

* feat: use select2 to fetch fk and qs objects from api ([`aa127b6`](https://github.com/bnznamco/django-structured-field/commit/aa127b64cf6783dc026434498ebc6242e0c1801f))

* feat: update jsonschema for fk and qs field to include select2 defs&#34; ([`c8715ef`](https://github.com/bnznamco/django-structured-field/commit/c8715ef14281229e2d77f2b17e42f43cb5ac013a))

* feat: update model search endpoint to admit direct pk searches ([`6987be0`](https://github.com/bnznamco/django-structured-field/commit/6987be0b20cbf059185259171fb974c859d2fccc))

* feat: add autocomplete to foreignkeys ([`c7cd96b`](https://github.com/bnznamco/django-structured-field/commit/c7cd96b0cf6ed22b6afd58a162a70c747457795e))

* feat: resolve forward ref in cache types eval ([`07ee16a`](https://github.com/bnznamco/django-structured-field/commit/07ee16acfaa0392868c37d537f78e2dbf7ef66cb))

* feat: handle errors in json editor ([`a3d3e7e`](https://github.com/bnznamco/django-structured-field/commit/a3d3e7e2505eca21f087eea7d3dd6508962a3c11))

* feat: better theming for tools modals in editor ([`62f0ab1`](https://github.com/bnznamco/django-structured-field/commit/62f0ab148c8daca1e6850017a213826dd1635a7c))

* feat: change background and border of nested json editors ([`533a657`](https://github.com/bnznamco/django-structured-field/commit/533a657a24529371b6baf74976bed35516c6004c))

* feat: change button style in editor ([`8ae4f66`](https://github.com/bnznamco/django-structured-field/commit/8ae4f668610ca6d429468bf6073a5314a44ea437))

* feat: added some styling to editor ([`c5d7988`](https://github.com/bnznamco/django-structured-field/commit/c5d7988ce126a225c6fa88bc58f97561e6867394))

* feat: added json editor in django admin ([`7d96762`](https://github.com/bnznamco/django-structured-field/commit/7d96762c24a0cecf4db3e75fde3f91bfc35ad780))

### Fix

* fix: fix get_type eval for python 3.8 ([`c0c132c`](https://github.com/bnznamco/django-structured-field/commit/c0c132c2be00e46faec0c68eb5ab4e0c3fa37402))

* fix: fix annotation inspection in base meta model ([`5ee16d7`](https://github.com/bnznamco/django-structured-field/commit/5ee16d758ab9b348756e987c05866a67154dbc8f))

* fix: fix search view not finding direct pks&#34; ([`0bf1bde`](https://github.com/bnznamco/django-structured-field/commit/0bf1bdeab55ffb4fb865f4f61ea1cb595e2dec9a))

* fix: fix qsfield serialization when dealink with list of pks ([`7c8cdad`](https://github.com/bnznamco/django-structured-field/commit/7c8cdad7c0039725353773d4beb1b607b98aab2e))

* fix: fix attribute changes on db coming data ([`74d02e4`](https://github.com/bnznamco/django-structured-field/commit/74d02e460045097fd456257d57d4031ed8856ef4))

* fix: fix response from search model api ([`24139ee`](https://github.com/bnznamco/django-structured-field/commit/24139eea2b2fa7e67b4f29c530889a2bdaa232e5))

* fix: fix error handling in fe json editor ([`cb38c17`](https://github.com/bnznamco/django-structured-field/commit/cb38c17b33e2bf873402e4846c29c5b9e8b2c129))

* fix: fix editor nested relation concurrency ([`1929be2`](https://github.com/bnznamco/django-structured-field/commit/1929be26bf5805ee5373b23fa1dbdf3e01a746b1))

* fix: fix cache engine not fetching pk in case of objects ([`4c4fb4d`](https://github.com/bnznamco/django-structured-field/commit/4c4fb4d3a8d5654f4c418a59e6bacbb4b2c82972))

* fix: fix cache on nested elements ([`c4f79ac`](https://github.com/bnznamco/django-structured-field/commit/c4f79ac0631f59c9f935770d0bb7189ca4e2cb2d))

* fix: fix typo in model form class name ([`e80b8e0`](https://github.com/bnznamco/django-structured-field/commit/e80b8e05d76e15c1001e7c34427da835452edbab))

* fix: fix sql errors in sqlite db ([`e3520bd`](https://github.com/bnznamco/django-structured-field/commit/e3520bdae313a3cd2d88397b098b87fbf54ccc6e))

* fix: fix typing errors for python 3.8 ([`5bbf3ec`](https://github.com/bnznamco/django-structured-field/commit/5bbf3ec149b0de3d3153455a080f50433985f5d5))

### Refactor

* refactor: refactor cache engine ([`f024362`](https://github.com/bnznamco/django-structured-field/commit/f024362918e4d1353080774e92c854e38d6c1325))

* refactor: refactor MetaModel class ([`70a03c7`](https://github.com/bnznamco/django-structured-field/commit/70a03c7842d965eed84af4b6ef8c285aad0dccd3))

* refactor: refactor search model api endpoint ([`3396fa6`](https://github.com/bnznamco/django-structured-field/commit/3396fa67b85f72d18b5c7b1f0a07ea9c063c2d48))

* refactor: move select2 scss code ([`cf79fb4`](https://github.com/bnznamco/django-structured-field/commit/cf79fb4743494b20003e92ae2710058200601489))

* refactor: correct typo in reactive form path map ([`03d3cb4`](https://github.com/bnznamco/django-structured-field/commit/03d3cb4f1f6fec9f5d5004e71735098bc94d049a))

* refactor: correct typo in reactive form path ([`dcf5444`](https://github.com/bnznamco/django-structured-field/commit/dcf5444a6450bd3dea1be667a48e76ae6c0f7ffd))

### Unknown

* tests: more tests ([`42a9021`](https://github.com/bnznamco/django-structured-field/commit/42a90218fddb2374e13dc024389136d7afa7cba2))

* tests: fix warnings in unit testing&#39; ([`2837ab0`](https://github.com/bnznamco/django-structured-field/commit/2837ab097dbd6150d4937f405e6eb243cb609b41))

* tests: update error mapper test ([`8ee2fe3`](https://github.com/bnznamco/django-structured-field/commit/8ee2fe3cf6dd56a1c5fc9fc9e3868c3fbffb3bd4))

* deps: update MANIFEST ([`4552d45`](https://github.com/bnznamco/django-structured-field/commit/4552d459c9e1331ca06cc3be652446af69c6d5e8))

* tests: 85% coverage reached :thumbs_up: 👍 ([`63277ea`](https://github.com/bnznamco/django-structured-field/commit/63277ea75d0dea85aeca845f25d658c59b4db2e0))

* Merge branch &#39;master&#39; into feature/editorautocomplete ([`7e638ab`](https://github.com/bnznamco/django-structured-field/commit/7e638abed8b1278d2174b5ffa90e4f0f21ad7521))

* tests: added new test case for qs_field changes persistence ([`474dbe0`](https://github.com/bnznamco/django-structured-field/commit/474dbe0070ac6a5d1e6d03222236ea1a0f6dfe42))

* deps: remove autocomplete dependency ([`86be78a`](https://github.com/bnznamco/django-structured-field/commit/86be78ac082a9c30d435732053605d31fea579e1))

* deps: update pydantic to 2.8 ([`77cee0b`](https://github.com/bnznamco/django-structured-field/commit/77cee0bb7244da32a785316b2e6ea7270e0dbadb))

* tests: scaffold for drf test and tests code clean ([`fb851a1`](https://github.com/bnznamco/django-structured-field/commit/fb851a1ee8dc77fba01b02e6fa801384211955c5))

* tests: refactor cache engine tests ([`6b29163`](https://github.com/bnznamco/django-structured-field/commit/6b29163a119a9d8073831174ff8ff2e20a3021ce))

* tests: create new tests for django admin widget ([`affe5ae`](https://github.com/bnznamco/django-structured-field/commit/affe5ae6b130ba19c657833d4a8b29b06d372efd))

* tests: more schematic tests subdivision and new test for qs cache ([`a67a3e2`](https://github.com/bnznamco/django-structured-field/commit/a67a3e2e7cbf69d8a3c70f368fae9ee9957957fb))

* tests: fix python 3.8 typing ([`d32880d`](https://github.com/bnznamco/django-structured-field/commit/d32880ddf5c4d007837840ce5e3f64bea326d6fe))

* tests: fix whitespace error ([`a2500f4`](https://github.com/bnznamco/django-structured-field/commit/a2500f408b67adf2c18a39e001a44b113b5d1804))

* tests: activate cache db hit test ([`e220f3b`](https://github.com/bnznamco/django-structured-field/commit/e220f3bef97fdd592f21361bd22938756d7efa04))

* tests: update test models and tescases ([`81c2d35`](https://github.com/bnznamco/django-structured-field/commit/81c2d3516fb15319ce71d7bf97a4caa49a07b1c6))

* tests: update test migrations ([`69164d7`](https://github.com/bnznamco/django-structured-field/commit/69164d7090b266b72d87fe60ae899b12d94d7fa8))
