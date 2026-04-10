import { useCallback } from 'react';

import handleSourceByHtmlLinkClick from './utils';

const useSourceByHtmlAnalytics = gaSpotlightAnalytics =>
    useCallback(
        clickEvent =>
            handleSourceByHtmlLinkClick(clickEvent, gaSpotlightAnalytics),
        [gaSpotlightAnalytics],
    );

export default useSourceByHtmlAnalytics;
