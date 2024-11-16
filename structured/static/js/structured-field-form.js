(function () {
    'use strict';

    function initCallbacks() {
        window.JSONEditor.defaults.callbacks = {
            "select2": {
                "createQueryParams": function (_editor, params) {
                    return {
                      _q: params.term, // search term
                      page: params.page || 1,
                    };
                  },
                "processResultData": function (_editor, data, params) {
                    params.page = params.page || 1;
                    return {
                        results: data.items.map(item => ({id: btoa(JSON.stringify(item)), text: item.name})),
                        pagination: {
                            more: data.more
                        }
                    };
                  },
            }
        };
    }

    function patchSelect2Editor() {
        window.JSONEditor.defaults.editors.select2 = class extends window.JSONEditor.defaults.editors.select2 {
            titleFieldsPriority = ['__str__', 'name', 'title', 'label', 'id']

            preBuild() {
                if (this.schema.type === "relation") {
                    this.schema.enum = [];
                }
                super.preBuild();
            }

            forceAddOption(value, text) {
                if (this.enum_values.includes(value)) return
                this.schema.enum.push(value);
                this.enum_values.push(value);
                this.enum_options.push(value);
                this.enum_display.push(text);
                this.theme.setSelectOptions(this.input, this.enum_options, this.enum_display);
            }

            isRelation() {
                return this.schema.type === "relation"
            }
            isManyRelation(value = []) {
                return this.isRelation() && this.schema.multiple && Array.isArray(value)
            }
            isClearable(value = null) {
                return this.isRelation() && this.schema.options.select2.allowClear && value === null
            }
            isObject(x) {
                return typeof x === 'object' && !Array.isArray(x) && x !== null
            }
            isString(x) {
                return typeof x === 'string'
            }
            isArray(x) {
                return Array.isArray(x)
            }
            isNumber(x) {
                return typeof x === 'number' || !isNaN(x)
            }
            isRelationObject(x) {
                return this.isObject(x) && x.id && x.model
            }
            isB64Encoded(x) {
                return this.isString(x) && x.match(/^[a-zA-Z0-9-_]+={0,2}$/)
            }
            isJSONString(x) {
                try {
                    return this.isString(x) && this.isObject(JSON.parse(x))
                } catch (e) {
                    return false
                }
            }
            isb64RelationObject(x) {
                if (this.isB64Encoded(x)) {
                    var decoded = atob(x);
                    return this.isJSONString(decoded) && this.isRelationObject(JSON.parse(decoded))
                }
                return false
            }
            decodeB64Object(x) {
                return this.isb64RelationObject(x) ? JSON.parse(atob(x)) : x
            }

            deserializeRelValue(value) {
                if (this.isManyRelation(value)) {
                    return value && value.map(val => this.deserializeRelValue(val))
                }
                else if (this.isRelationObject(value)) {
                    return value
                }
                else if (this.isJSONString(value)) {
                    return JSON.parse(value)
                }
                else if (this.isb64RelationObject(value)) {
                    return this.decodeB64Object(value)
                }
                return value
            }

            serializeRelValue(value) {
                if (this.isManyRelation(value)) {
                    return value.map(val => this.serializeRelValue(val))
                }
                else if (this.isRelationObject(value)) {
                    let name = value[this.titleFieldsPriority.find(field => value[field])];
                    let serialized = JSON.stringify(value);
                    this.forceAddOption(serialized, name);
                    return serialized
                }
                else if (this.isJSONString(value)) {
                    return this.serializeRelValue(JSON.parse(value))
                } else if (this.isb64RelationObject(value)) {
                    return value
                }
                return value
            }

            typecast(value) {
                if (this.isRelation()) {
                    if (this.isManyRelation(value)) {
                        return value.map(val => val && this.serializeRelValue(val))
                    } else if (this.isClearable(value)) {
                        return null
                    }
                }
                return super.typecast(value)
            }

            updateValue(value) {
                if (this.isRelation()) {
                    if (this.isClearable(value)) {
                        this.value = null;
                        return this.value
                    }
                    this.value = this.serializeRelValue(value);
                    return this.value
                }
                return super.updateValue(value)
            }

            getValue() {
                if (this.isRelation()) {
                    return this.deserializeRelValue(this.value)
                }
                return super.getValue()
            }

            async setValue(value, initial) {
                if (this.isRelation()) {
                    value = this.updateValue(value);
                    while (!this.select2_instance) {
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                }
                return super.setValue(value, initial)
            }

            afterInputReady() {
                super.afterInputReady();
                if (this.isRelation()) {
                    this.newEnumAllowed = true;
                    this.control?.querySelector('.select2-container')?.removeAttribute('style');
                }
            }
        };
        window.JSONEditor.defaults.resolvers.unshift(function (schema) {
            if (schema.type === "relation" && schema.format === "select2") {
                return "select2"
            }
        });
    }

    function renderForm(element) {
        const schema = JSON.parse(element.dataset.schema);
        console.log("🧱 schema", schema);
        JSON.parse(element.dataset.uischema);
        const formData = JSON.parse(element.dataset.formdata);
        console.log("🫐 formData", formData);
        const inputTextArea = document.getElementById(`id_${element.dataset.name}`);
        const editor = new JSONEditor(element, { 
            schema,
            startval: formData,
            max_depth: 10,
            show_errors: 'always',
        });
        editor.on('change', () => {
            inputTextArea.innerHTML = JSON.stringify(editor.getValue());
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        JSONEditor.defaults.options.theme = 'html';
        JSONEditor.defaults.options.iconlib = 'fontawesome5';
        initCallbacks();
        patchSelect2Editor();
        const elements = document.querySelectorAll('.structured-field-editor');
        for (let i = 0; i < elements.length; i++) {
            renderForm(elements[i]);
        }
    });

})();
//# sourceMappingURL=structured-field-form.js.map
