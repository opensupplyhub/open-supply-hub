'use strict';

export const handler = async (event) => {
    const request = event.Records[0].cf.request;
    if (request.uri === '/') {
        request.uri = '/index.html';
    }
    return request;
}
