(function () {
    'use strict';

    function renderForm(element) {
      const schema = JSON.parse(element.dataset.schema);
      JSON.parse(element.dataset.uischema);
      const formData = JSON.parse(element.dataset.formdata);
      const inputTextArea = document.getElementById(`id_${element.dataset.name}`);
      const editor = new JSONEditor(element, {
        schema,
        startval: formData,
        max_depth: 10,
        show_opt_in: true,
        disable_properties: true,
        disable_edit_json: true,
        disable_collapse: true,
        object_layout: 'table'
      });
      editor.on('change', () => {
        inputTextArea.innerHTML = JSON.stringify(editor.getValue());
      });
    }
    document.addEventListener('DOMContentLoaded', () => {
      const elements = document.querySelectorAll('.structured-field-editor');
      for (let i = 0; i < elements.length; i++) {
        renderForm(elements[i]);
      }
    });

})();
