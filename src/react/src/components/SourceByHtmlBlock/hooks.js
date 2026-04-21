import { useCallback } from 'react';

import handleSourceByHtmlLinkClick from './utils';
import useViewerUserIdForAnalytics from '../../util/analytics/hooks';

const useSourceByHtmlAnalytics = gaSpotlightAnalytics => {
    const viewerUserId = useViewerUserIdForAnalytics();
    return useCallback(
        clickEvent =>
            handleSourceByHtmlLinkClick(
                clickEvent,
                gaSpotlightAnalytics,
                viewerUserId,
            ),
        [gaSpotlightAnalytics, viewerUserId],
    );
};

export default useSourceByHtmlAnalytics;
