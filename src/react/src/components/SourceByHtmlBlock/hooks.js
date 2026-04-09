import { useCallback } from 'react';

import handleSourceByHtmlLinkClick from './utils';

const useSourceByHtmlAnalytics = gaSpotlightAnalytics =>
    useCallback(
        event => handleSourceByHtmlLinkClick(event, gaSpotlightAnalytics),
        [gaSpotlightAnalytics],
    );

export default useSourceByHtmlAnalytics;
