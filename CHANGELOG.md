# CHANGELOG



## v0.2.1 (2024-11-15)

### Fix

* fix(admin): fix m2m empty value ([`99c0404`](https://github.com/lotrekagency/django-structured-field/commit/99c04046c0913cac341c46548c651129bae9c471))


## v0.2.0 (2024-10-26)

### Chore

* chore: update ci testing codecov upload ([`593947d`](https://github.com/lotrekagency/django-structured-field/commit/593947dbbf3df86770b59cf8f6db7bd5f70ef303))

### Documentation

* docs: update readme admin and restframework integrations ([`d4f84d8`](https://github.com/lotrekagency/django-structured-field/commit/d4f84d82301dad3affe5e6e10ca07b7b93f0d2f0))

* docs: update readme shields ([`68f363a`](https://github.com/lotrekagency/django-structured-field/commit/68f363aae9f5ac7e23f0197baaf7c38263db1b7f))

### Feature

* feat(admin): added compatibility for Queryset field in admin ([`5cc6aa2`](https://github.com/lotrekagency/django-structured-field/commit/5cc6aa2ddf59010a25c7f5116cb9bcbcbe769456))

* feat(admin): make relations nullable in json-form schema ([`3763192`](https://github.com/lotrekagency/django-structured-field/commit/376319254ad00f9e03e9b403c0adc202ba6c600a))

* feat(core): added compatibility with abstract model relations ([`8e0d6c1`](https://github.com/lotrekagency/django-structured-field/commit/8e0d6c1f6efaf3a979642b63fee59ae369e97a62))

* feat(admin): better search capabilities for admin panel ([`a782592`](https://github.com/lotrekagency/django-structured-field/commit/a782592eb19dd39c600c9021f96c00e478fc3b7a))

### Fix

* fix(admin): fix widget wrong method alias &#39;model_json_schema&#39; ([`028dae9`](https://github.com/lotrekagency/django-structured-field/commit/028dae94282b0492d8221f5b978d87b63efd9d30))

* fix(field): fix structured field typing annotations import ([`de088ac`](https://github.com/lotrekagency/django-structured-field/commit/de088ac02a4dac5bae7dd462f09bdb5abdb75634))

### Refactor

* refactor(admin): remove unused js ([`86b5a38`](https://github.com/lotrekagency/django-structured-field/commit/86b5a38ce86bd3b5d78ec1b34a7549211fd5c66b))

### Unknown

* deps(jsoneditor): update jsoneditor version ([`8ecf724`](https://github.com/lotrekagency/django-structured-field/commit/8ecf724e603072b274a7eaa2a06e7020407472ae))


## v0.1.0 (2024-07-12)

### Chore

* chore: limit compatibility to python &gt;= 3.9 ([`b7754ad`](https://github.com/lotrekagency/django-structured-field/commit/b7754ada06443517846b1a185ccd8a9e4470cc1b))

* chore: better typing suggestions for cache enabled models ([`0cb660e`](https://github.com/lotrekagency/django-structured-field/commit/0cb660e814c9ab95c8235344797fcf9f1accb3ba))

* chore: fix typing error on ci tests ([`d3be04e`](https://github.com/lotrekagency/django-structured-field/commit/d3be04e3c849ca27822f904ace2defec76a8b97c))

* chore: fir typo in requirements.txt ([`62a56df`](https://github.com/lotrekagency/django-structured-field/commit/62a56df244486aeb74c59390edb9c2f0f7130ee8))

* chore: update ci testing versions ([`0d2cae1`](https://github.com/lotrekagency/django-structured-field/commit/0d2cae16adfc2536a3df23670d7e90c039df62f2))

* chore: update ci testing versions ([`e35f276`](https://github.com/lotrekagency/django-structured-field/commit/e35f276f13246bb0c30510e6f14f49f63849c454))

* chore: fix rollup watching ([`43f016c`](https://github.com/lotrekagency/django-structured-field/commit/43f016c7899c55ddd59ab49f5f9a9c9d3cc69804))

* chore: change js form placeholder for qs ([`4ca997d`](https://github.com/lotrekagency/django-structured-field/commit/4ca997d5c0bc4cfbb4ce5b296cc400f59080a9af))

* chore: remove structured model form ([`78fdcf2`](https://github.com/lotrekagency/django-structured-field/commit/78fdcf241e61b7eb63501053519fa1d60abc4cd3))

* chore: added jsoneditor.js.map ([`cdaa86d`](https://github.com/lotrekagency/django-structured-field/commit/cdaa86d847bf8e732d6fa3f678ab066aec4039ab))

* chore: first commit 🙀 ([`9a29807`](https://github.com/lotrekagency/django-structured-field/commit/9a2980781c45b9b075f9451207221219356e9572))

### Documentation

* docs: update readme settings section 🐸 ([`1d2d5bd`](https://github.com/lotrekagency/django-structured-field/commit/1d2d5bddc304561c7a6d245690e1650c3b73a20c))

* docs: update readme 🐸 ([`8afe82b`](https://github.com/lotrekagency/django-structured-field/commit/8afe82b27763dd3efd65f707b9c9ded653dba30f))

* docs: update README 📒 ([`f2dc816`](https://github.com/lotrekagency/django-structured-field/commit/f2dc8164d95d4598597fa2e8842002ba40a86119))

* docs: update README 📒 ([`933ebb5`](https://github.com/lotrekagency/django-structured-field/commit/933ebb504956e80653a806a016f64012af6bdc5a))

### Feature

* feat: added settings to enable shared cache experimental features ([`535ada5`](https://github.com/lotrekagency/django-structured-field/commit/535ada5fbf301b2084957c71b82d6dba795b790f))

* feat: first draft for a shared cache between instances and fields ([`5862559`](https://github.com/lotrekagency/django-structured-field/commit/58625597e8cfe82bd4c3ea7c61656c42220d981d))

* feat: better visibility for autocomplete selected item in multiple relations ([`20f6497`](https://github.com/lotrekagency/django-structured-field/commit/20f649757fc6e18813a784fe3af4d16bbe7a27b9))

* feat: better visibility to selected option in m2m fields editor ([`7b16dae`](https://github.com/lotrekagency/django-structured-field/commit/7b16dae4f92c7a34daa13706650b5e7f74ed2e31))

* feat: adapt dark schema css ([`11621ca`](https://github.com/lotrekagency/django-structured-field/commit/11621ca460c72ed2009c4611ea431f5ab73dce6b))

* feat: use select2 to fetch fk and qs objects from api ([`aa127b6`](https://github.com/lotrekagency/django-structured-field/commit/aa127b64cf6783dc026434498ebc6242e0c1801f))

* feat: update jsonschema for fk and qs field to include select2 defs&#34; ([`c8715ef`](https://github.com/lotrekagency/django-structured-field/commit/c8715ef14281229e2d77f2b17e42f43cb5ac013a))

* feat: update model search endpoint to admit direct pk searches ([`6987be0`](https://github.com/lotrekagency/django-structured-field/commit/6987be0b20cbf059185259171fb974c859d2fccc))

* feat: add autocomplete to foreignkeys ([`c7cd96b`](https://github.com/lotrekagency/django-structured-field/commit/c7cd96b0cf6ed22b6afd58a162a70c747457795e))

* feat: resolve forward ref in cache types eval ([`07ee16a`](https://github.com/lotrekagency/django-structured-field/commit/07ee16acfaa0392868c37d537f78e2dbf7ef66cb))

* feat: handle errors in json editor ([`a3d3e7e`](https://github.com/lotrekagency/django-structured-field/commit/a3d3e7e2505eca21f087eea7d3dd6508962a3c11))

* feat: better theming for tools modals in editor ([`62f0ab1`](https://github.com/lotrekagency/django-structured-field/commit/62f0ab148c8daca1e6850017a213826dd1635a7c))

* feat: change background and border of nested json editors ([`533a657`](https://github.com/lotrekagency/django-structured-field/commit/533a657a24529371b6baf74976bed35516c6004c))

* feat: change button style in editor ([`8ae4f66`](https://github.com/lotrekagency/django-structured-field/commit/8ae4f668610ca6d429468bf6073a5314a44ea437))

* feat: added some styling to editor ([`c5d7988`](https://github.com/lotrekagency/django-structured-field/commit/c5d7988ce126a225c6fa88bc58f97561e6867394))

* feat: added json editor in django admin ([`7d96762`](https://github.com/lotrekagency/django-structured-field/commit/7d96762c24a0cecf4db3e75fde3f91bfc35ad780))

### Fix

* fix: fix get_type eval for python 3.8 ([`c0c132c`](https://github.com/lotrekagency/django-structured-field/commit/c0c132c2be00e46faec0c68eb5ab4e0c3fa37402))

* fix: fix annotation inspection in base meta model ([`5ee16d7`](https://github.com/lotrekagency/django-structured-field/commit/5ee16d758ab9b348756e987c05866a67154dbc8f))

* fix: fix search view not finding direct pks&#34; ([`0bf1bde`](https://github.com/lotrekagency/django-structured-field/commit/0bf1bdeab55ffb4fb865f4f61ea1cb595e2dec9a))

* fix: fix qsfield serialization when dealink with list of pks ([`7c8cdad`](https://github.com/lotrekagency/django-structured-field/commit/7c8cdad7c0039725353773d4beb1b607b98aab2e))

* fix: fix attribute changes on db coming data ([`74d02e4`](https://github.com/lotrekagency/django-structured-field/commit/74d02e460045097fd456257d57d4031ed8856ef4))

* fix: fix response from search model api ([`24139ee`](https://github.com/lotrekagency/django-structured-field/commit/24139eea2b2fa7e67b4f29c530889a2bdaa232e5))

* fix: fix error handling in fe json editor ([`cb38c17`](https://github.com/lotrekagency/django-structured-field/commit/cb38c17b33e2bf873402e4846c29c5b9e8b2c129))

* fix: fix editor nested relation concurrency ([`1929be2`](https://github.com/lotrekagency/django-structured-field/commit/1929be26bf5805ee5373b23fa1dbdf3e01a746b1))

* fix: fix cache engine not fetching pk in case of objects ([`4c4fb4d`](https://github.com/lotrekagency/django-structured-field/commit/4c4fb4d3a8d5654f4c418a59e6bacbb4b2c82972))

* fix: fix cache on nested elements ([`c4f79ac`](https://github.com/lotrekagency/django-structured-field/commit/c4f79ac0631f59c9f935770d0bb7189ca4e2cb2d))

* fix: fix typo in model form class name ([`e80b8e0`](https://github.com/lotrekagency/django-structured-field/commit/e80b8e05d76e15c1001e7c34427da835452edbab))

* fix: fix sql errors in sqlite db ([`e3520bd`](https://github.com/lotrekagency/django-structured-field/commit/e3520bdae313a3cd2d88397b098b87fbf54ccc6e))

* fix: fix typing errors for python 3.8 ([`5bbf3ec`](https://github.com/lotrekagency/django-structured-field/commit/5bbf3ec149b0de3d3153455a080f50433985f5d5))

### Refactor

* refactor: refactor cache engine ([`f024362`](https://github.com/lotrekagency/django-structured-field/commit/f024362918e4d1353080774e92c854e38d6c1325))

* refactor: refactor MetaModel class ([`70a03c7`](https://github.com/lotrekagency/django-structured-field/commit/70a03c7842d965eed84af4b6ef8c285aad0dccd3))

* refactor: refactor search model api endpoint ([`3396fa6`](https://github.com/lotrekagency/django-structured-field/commit/3396fa67b85f72d18b5c7b1f0a07ea9c063c2d48))

* refactor: move select2 scss code ([`cf79fb4`](https://github.com/lotrekagency/django-structured-field/commit/cf79fb4743494b20003e92ae2710058200601489))

* refactor: correct typo in reactive form path map ([`03d3cb4`](https://github.com/lotrekagency/django-structured-field/commit/03d3cb4f1f6fec9f5d5004e71735098bc94d049a))

* refactor: correct typo in reactive form path ([`dcf5444`](https://github.com/lotrekagency/django-structured-field/commit/dcf5444a6450bd3dea1be667a48e76ae6c0f7ffd))

### Unknown

* tests: more tests ([`42a9021`](https://github.com/lotrekagency/django-structured-field/commit/42a90218fddb2374e13dc024389136d7afa7cba2))

* tests: fix warnings in unit testing&#39; ([`2837ab0`](https://github.com/lotrekagency/django-structured-field/commit/2837ab097dbd6150d4937f405e6eb243cb609b41))

* tests: update error mapper test ([`8ee2fe3`](https://github.com/lotrekagency/django-structured-field/commit/8ee2fe3cf6dd56a1c5fc9fc9e3868c3fbffb3bd4))

* deps: update MANIFEST ([`4552d45`](https://github.com/lotrekagency/django-structured-field/commit/4552d459c9e1331ca06cc3be652446af69c6d5e8))

* tests: 85% coverage reached :thumbs_up: 👍 ([`63277ea`](https://github.com/lotrekagency/django-structured-field/commit/63277ea75d0dea85aeca845f25d658c59b4db2e0))

* Merge branch &#39;master&#39; into feature/editorautocomplete ([`7e638ab`](https://github.com/lotrekagency/django-structured-field/commit/7e638abed8b1278d2174b5ffa90e4f0f21ad7521))

* tests: added new test case for qs_field changes persistence ([`474dbe0`](https://github.com/lotrekagency/django-structured-field/commit/474dbe0070ac6a5d1e6d03222236ea1a0f6dfe42))

* deps: remove autocomplete dependency ([`86be78a`](https://github.com/lotrekagency/django-structured-field/commit/86be78ac082a9c30d435732053605d31fea579e1))

* deps: update pydantic to 2.8 ([`77cee0b`](https://github.com/lotrekagency/django-structured-field/commit/77cee0bb7244da32a785316b2e6ea7270e0dbadb))

* tests: scaffold for drf test and tests code clean ([`fb851a1`](https://github.com/lotrekagency/django-structured-field/commit/fb851a1ee8dc77fba01b02e6fa801384211955c5))

* tests: refactor cache engine tests ([`6b29163`](https://github.com/lotrekagency/django-structured-field/commit/6b29163a119a9d8073831174ff8ff2e20a3021ce))

* tests: create new tests for django admin widget ([`affe5ae`](https://github.com/lotrekagency/django-structured-field/commit/affe5ae6b130ba19c657833d4a8b29b06d372efd))

* tests: more schematic tests subdivision and new test for qs cache ([`a67a3e2`](https://github.com/lotrekagency/django-structured-field/commit/a67a3e2e7cbf69d8a3c70f368fae9ee9957957fb))

* tests: fix python 3.8 typing ([`d32880d`](https://github.com/lotrekagency/django-structured-field/commit/d32880ddf5c4d007837840ce5e3f64bea326d6fe))

* tests: fix whitespace error ([`a2500f4`](https://github.com/lotrekagency/django-structured-field/commit/a2500f408b67adf2c18a39e001a44b113b5d1804))

* tests: activate cache db hit test ([`e220f3b`](https://github.com/lotrekagency/django-structured-field/commit/e220f3bef97fdd592f21361bd22938756d7efa04))

* tests: update test models and tescases ([`81c2d35`](https://github.com/lotrekagency/django-structured-field/commit/81c2d3516fb15319ce71d7bf97a4caa49a07b1c6))

* tests: update test migrations ([`69164d7`](https://github.com/lotrekagency/django-structured-field/commit/69164d7090b266b72d87fe60ae899b12d94d7fa8))
