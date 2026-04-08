(function () {
  'use strict';

  StructuredWidgetEditor.registerCustomElement('schema-form');


  function renderForm(element) {
    var schema = structuredFields[element.dataset.name].schema;
    var formData = structuredFields[element.dataset.name].formData;
    // var uiSchema = structuredFields[element.dataset.name].uiSchema;
    var errors = structuredFields[element.dataset.name].errors;
    var language = structuredFields[element.dataset.name].language || '';
    var inputTextArea = document.getElementById('id_' + element.dataset.name);

    var schemaForm = document.createElement('schema-form');
    schemaForm.schema = schema;
    schemaForm.initialData = formData;
    schemaForm.errors = errors;
    schemaForm.language = language;

    schemaForm.addEventListener('change', function (e) {
        if (e.detail && e.detail[0]) {
            inputTextArea.textContent = JSON.stringify(e.detail[0]);
        }
    });

    element.appendChild(schemaForm);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var elements = document.querySelectorAll('.structured-field-editor');
    for (var i = 0; i < elements.length; i++) {
      renderForm(elements[i]);
    }
  });
})();
