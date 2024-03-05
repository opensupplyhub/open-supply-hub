import '@testing-library/jest-dom';
import { JSDOM } from 'jsdom';

const customJestEnvironment = async () => {
    const jsdom = new JSDOM('<!doctype html><html><body></body></html>', {
        url: 'http://localhost',
    });

    global.window = jsdom.window;
    global.document = jsdom.window.document;
    global.navigator = jsdom.window.navigator;
    global.btoa = (str) => Buffer.from(str, 'binary').toString('base64');
    global.atob = (str) => Buffer.from(str, 'base64').toString('binary');
};

customJestEnvironment();
