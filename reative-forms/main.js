import './scss/main.scss';
import { initCallbacks } from './callbacks';

function renderForm(element) {
    const schema = JSON.parse(element.dataset.schema);
    const uiSchema = JSON.parse(element.dataset.uischema);
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