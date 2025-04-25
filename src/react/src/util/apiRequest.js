import axios from 'axios';
import { CSRF_TOKEN_KEY } from './constants';

// A legacy user CSRF token implementation is needed to prevent
// functional issues until the next session expiration.
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
const apiRequest = axios.create({
    headers: {
        credentials: 'same-origin',
    },
});

// Appropriate place to set the client key header 'X-OAR-Client-Key'
// used to authenticate anonymous API requests.
// Set 'X-CSRFToken' for CSRF protection when
// making unsafe HTTP requests.
apiRequest.interceptors.request.use(config => {
    const headers = {
        ...config.headers,
        'X-OAR-Client-Key': window.ENVIRONMENT.OAR_CLIENT_KEY,
        'X-CSRFToken':
            window.localStorage.getItem(CSRF_TOKEN_KEY) ||
            config.headers['X-CSRFToken'] ||
            undefined,
    };

    return { ...config, headers };
});

export default apiRequest;
