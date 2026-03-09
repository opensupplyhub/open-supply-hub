// Node 14 does not expose TextEncoder/TextDecoder as globals; jsdom 18
// requires them. Polyfill before jsdom is loaded. Must use require() here
// because ES `import` statements are hoisted above any code by Babel, which
// would make the polyfill arrive too late.
/* eslint-disable global-require */
const { TextEncoder: NodeTextEncoder, TextDecoder: NodeTextDecoder } = require('util');

global.TextEncoder = global.TextEncoder || NodeTextEncoder;
global.TextDecoder = global.TextDecoder || NodeTextDecoder;

require('@testing-library/jest-dom');

const { JSDOM } = require('jsdom');
/* eslint-enable global-require */

const customJestEnvironment = async () => {
    const jsdom = new JSDOM('<!doctype html><html><body></body></html>', {
        url: 'http://localhost',
    });

    global.window = jsdom.window;
    global.document = jsdom.window.document;
    global.navigator = jsdom.window.navigator;
    global.btoa = str => Buffer.from(str, 'binary').toString('base64');
    global.atob = str => Buffer.from(str, 'base64').toString('binary');
};

customJestEnvironment();
