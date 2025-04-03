import axios from 'axios';

// Used to make authenticated HTTP requests to Django
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
const apiRequest = axios.create({
    headers: {
        credentials: 'same-origin',
    },
});

// Not related to CSRF protection, but this is the appropriate place to set the
// client key header used to authenticate anonymous API requests.
apiRequest.interceptors.request.use(config => {
    const headers = { ...config.headers };
    headers['X-OAR-Client-Key'] = window.ENVIRONMENT.OAR_CLIENT_KEY;

    if (!headers['X-CSRFToken']) {
        const csrfToken = window.localStorage.getItem('csrfToken');
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
    }

    return { ...config, headers };
});

export default apiRequest;
