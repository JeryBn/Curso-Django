import React from 'react';
import { createRoot } from 'react-dom/client';

createRoot(document.getElementById('root')).render(<ul>{['A','B'].map(item => <li>{item}</li>)}</ul>);
