import React from 'react';
import { InfoLink, InfoPaths } from '../util/constants';

const CookiePreferencesText = () => (
    <div>
        We use cookies to give you the best experience on Open Supply Hub and
        understand site performance. By accepting, you consent to our use of
        cookies and other analytics tools according to our{' '}
        <a
            href={`${InfoLink}/${InfoPaths.termsOfService}`}
            target="_blank"
            rel="noreferrer"
        >
            privacy policy
        </a>{' '}
        .
    </div>
);

export default CookiePreferencesText;
