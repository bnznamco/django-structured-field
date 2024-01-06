import VueForm, { i18n } from '@lljj/vue3-form-naive';
import { createApp, h } from 'vue';
import naive from 'naive-ui'
import localizeEn from 'ajv-i18n/localize/en';



function renderForm(element) {
  const schema = JSON.parse(element.dataset.schema);
  const uiSchema = JSON.parse(element.dataset.uischema);
  const formData = JSON.parse(element.dataset.formdata);
  const inputTextArea = document.getElementById(`id_${element.dataset.name}`);
  i18n.useLocal(localizeEn);
  const vueApp = createApp({
    render() {
      return h(VueForm, {
        schema: schema,
        value: formData,
        "on-change": (value) => {
          console.log(value);
          inputTextArea.value = JSON.stringify(value);
        }
      })
    }
  });
  vueApp.use(naive);
  vueApp.mount(element);

}

document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('.structured-field-editor');
  for (let i = 0; i < forms.length; i++) {
    renderForm(forms[i]);
  }
});