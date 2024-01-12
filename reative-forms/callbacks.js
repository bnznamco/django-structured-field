export function initCallbacks() {
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
                    }).then(resolve)
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
