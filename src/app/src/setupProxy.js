const proxy = require('http-proxy-middleware');
const _ = require('lodash');

const pathsToProxy = Object.freeze([
    '/api',
    '/web',
    '/api-auth',
    '/rest-auth',
    '/user-login',
    '/user-logout',
    '/user-signup',
    '/user-profile',
    '/api-token-auth',
    '/api-feature-flags',
    '/tile',
]);

const pathsCCToProxy = Object.freeze(['/cc']);

const djangoProxyTarget = Object.freeze({ target: 'http://django:8081' });
const contriCleanerProxyTarget = Object.freeze({
    target: 'http://contricleaner:80',
});

const createProxies = function (app) {
    const proxies = _.forEach(pathsToProxy, path =>
        app.use(proxy(path, djangoProxyTarget)),
    );
    const ccProxies = _.forEach(pathsCCToProxy, path =>
        app.use(proxy(path, contriCleanerProxyTarget)),
    );
    return _.merge(proxies, ccProxies);
};

module.exports = createProxies;
