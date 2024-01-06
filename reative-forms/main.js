import React, { createElement, useState } from 'react';
import { JsonForms } from '@jsonforms/react';

import { createRoot } from 'react-dom/client';
import {
    materialRenderers,
    materialCells,
} from '@jsonforms/material-renderers';


function renderForm(form) {
    const schema = JSON.parse(form.dataset.schema);
    const uiSchema = JSON.parse(form.dataset.uischema);
    const formData = JSON.parse(form.dataset.formdata);
    const inputTextArea = document.getElementById(`id_${form.dataset.name}`);


    function App() {
        const [data, setData] = useState(formData);
        return (
          <div className='App'>
            <JsonForms
              schema={schema}
              data={data}
              renderers={materialRenderers}
              cells={materialCells}
              onChange={({ data, errors }) => setData(data)}
            />
          </div>
        );
      }
    
    const root = createRoot(form);


    root.render(createElement(App));
}

document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('.structured-field-editor');
    for (let i = 0; i < forms.length; i++) {
        renderForm(forms[i]);
    }
});