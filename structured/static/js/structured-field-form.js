(function () {
    'use strict';

    function initCallbacks() {
        window.JSONEditor.defaults.callbacks = {
            "autocomplete": {
                "search_model": function search(autocomplete_editor, input) {

                    const { model } = autocomplete_editor.schema.options.autocomplete;
                    var url = `/structured_field/search_model/?_m=${model}&_q=${encodeURI(input)}`;

                    return new Promise(function (resolve) {
                        if (input.length < 3) {
                            return resolve([]);
                        }

                        fetch(url).then(function (response) {
                            return response.json();
                        }).then(resolve);
                    });
                },
                "getResultValue_model": function getResultValue(autocomplete_editor, result) {
                    return result.name;
                },
                "renderResult_model": function (autocomplete_editor, result, props) {
                    return [
                        '<li ' + props + '>',
                        '<div class="model-name">' + result.name + '</div>',
                        '</li>'
                    ].join('');
                },
            }
        };
    }

    function renderForm(element) {
        const schema = JSON.parse(element.dataset.schema);
        JSON.parse(element.dataset.uischema);
        const formData = JSON.parse(element.dataset.formdata);
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
        const elements = document.querySelectorAll('.structured-field-editor');
        for (let i = 0; i < elements.length; i++) {
            renderForm(elements[i]);
        }
    });

})();
//# sourceMappingURL=structured-field-form.js.map
