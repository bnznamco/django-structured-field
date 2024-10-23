export function patchSelect2Editor() {
    window.JSONEditor.defaults.editors.select2 = class extends window.JSONEditor.defaults.editors.select2 {
        titleFieldsPriority = ['__str__', 'name', 'title', 'label', 'id']

        preBuild() {
            if (this.schema.type === "relation") {
                this.schema.enum = []
            }
            super.preBuild()
        }

        async fetchDataFromAPI(value) {
            value = Array.isArray(value) ? value.join(",") : value
            const url = `${this.options.select2.ajax.url}?_q=_pk__in=${value}`
            return await fetch(url).then(res => res.json()).catch(_ => [])
        }

        forceAddOption(value, text) {
            if (this.enum_values.includes(value)) return
            this.enum_values.push(value)
            this.enum_options.push(value)
            this.enum_display.push(text)
            this.theme.setSelectOptions(this.input, this.enum_options, this.enum_display)
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
                var decoded = atob(x)
                return this.isJSONString(decoded) && this.isRelationObject(JSON.parse(decoded))
            }
            return false
        }
        decodeB64Object(x) {
            return this.isb64RelationObject(x) ? JSON.parse(atob(x)) : x
        }

        setValue(value, initial) {
            if (this.schema.type === "relation") {
                if (this.schema.multiple && Array.isArray(value)) {
                    if (!value.length) return
                    value.forEach((val) => {
                        if (this.isb64RelationObject(val)) {
                            val = this.decodeB64Object(val)
                        }
                        let name = val[this.titleFieldsPriority.find(field => val[field])]
                        this.forceAddOption(JSON.stringify(val), name)
                    })
                    return super.setValue(value.map(val => JSON.stringify(val)), initial)
                }
                else if (this.isRelationObject(value)) {
                    let name = value[this.titleFieldsPriority.find(field => value[field])]
                    this.forceAddOption(JSON.stringify(value), name)
                    return super.setValue(JSON.stringify(value), initial)
                }
                else if (this.isb64RelationObject(value)) {
                    value = this.decodeB64Object(value)
                    this.setValue(value, initial)
                } else if (this.isJSONString(value)) {
                    value = JSON.parse(value)
                    this.setValue(value, initial)
                }
            }
            super.setValue(value, initial)
        }

        getValue() {
            if (this.schema.type === "relation") {
                if (!this.dependenciesFulfilled) {
                    return undefined
                }
                if (this.schema.multiple) {
                    return this.isArray(this.value) ? this.value?.map(val => this.typecast(val)) : this.value ? [this.typecast(this.value)] : []
                }
                else if (this.isb64RelationObject(this.value)) {
                    return this.decodeB64Object(this.value)
                }
                else if (this.isRelationObject(this.value)) {
                    return this.value
                } else if (this.isJSONString(this.value)) {
                    return JSON.parse(this.value)
                }
                return this.typecast(this.value)
            }
            return super.getValue()
        }

        afterInputReady() {
            super.afterInputReady()
            if (this.schema.type === "relation") {
                this.newEnumAllowed = true
                this.control?.querySelector('.select2-container')?.removeAttribute('style')
            }
        }
    }
    window.JSONEditor.defaults.resolvers.unshift(function (schema) {
        if (schema.type === "relation" && schema.format === "select2") {
            return "select2"
        }
    })
}
