export function initCallbacks() {
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
