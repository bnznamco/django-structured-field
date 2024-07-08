import './scss/main.scss';
import { initCallbacks } from './callbacks';
import { patchSelect2Editor } from './patches';

function renderForm(element) {
    const schema = JSON.parse(element.dataset.schema);
    console.log("🧱 schema", schema)
    const uiSchema = JSON.parse(element.dataset.uischema);
    const formData = JSON.parse(element.dataset.formdata);
    console.log("🫐 formData", formData)
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