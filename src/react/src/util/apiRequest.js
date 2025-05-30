import axios from 'axios';

const apiRequest = axios.create({
    headers: {
        credentials: 'same-origin',
    },
});

// Appropriate place to set the client key header 'X-OAR-Client-Key'
// used to authenticate anonymous API requests.
apiRequest.interceptors.request.use(config => {
    const headers = {
        ...config.headers,
        'X-OAR-Client-Key': window.ENVIRONMENT.OAR_CLIENT_KEY,
    };

    return { ...config, headers };
});

export default apiRequest;
