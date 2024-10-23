export function initCallbacks() {
    window.JSONEditor.defaults.callbacks = {
        "select2": {
            "createQueryParams": function (_editor, params) {
                return {
                  _q: params.term, // search term
                  page: params.page
                };
              },
            "processResultData": function (_editor, data, params) {
                return {
                    results: data.map(item =>  ({id: btoa(JSON.stringify(item)), text: item.name})),
                    pagination: {
                        more: false
                    }
                };
              },
        }
    };
}
