// polyfills for IE11
import 'core-js';
import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';
import { store } from './configureStore';
import './index.css';
import App from './App';

render(
    <Provider store={store}>
        <App />
    </Provider>,
    document.getElementById('root'),
);

// A service worker was registered by earlier versions of this app (CRA
// default). Keep unregistering so returning visitors drop the stale cache.
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
        .then(registration => {
            registration.unregister();
        })
        .catch(() => {});
}
