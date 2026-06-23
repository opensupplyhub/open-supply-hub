'use strict';

export const handler = async (event) => {
    const request = event.Records[0].cf.request;

    // Do not rewrite the exact root path — when enable_homepage_proxy is active,
    // the ordered cache behavior for "/" routes this to the Craft CMS origin.
    // Without this guard, the Lambda would rewrite "/" to "/index.html" and
    // break the Craft proxy if this behavior ever runs for the root path.
    if (request.uri === '/') {
        return request;
    }

    if (!request.uri.includes('.')) {
        request.uri = '/index.html';
    }

    return request;
}
