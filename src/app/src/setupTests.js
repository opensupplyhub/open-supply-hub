import '@testing-library/jest-dom';
import { JSDOM } from 'jsdom';

const customJestEnvironment = async () => {
    const jsdom = new JSDOM('<!doctype html><html><body></body></html>', {
        url: 'http://localhost',
    });

    global.window = jsdom.window;
    global.document = jsdom.window.document;
    global.navigator = jsdom.window.navigator;
};

customJestEnvironment();
