'use strict';

export const handler = async (event) => {
    const request = event.Records[0].cf.request;
    if (!request.uri.includes('.')) {
        request.uri = '/index.html';
    }
    return request;
}
