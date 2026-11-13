import { useEffect } from 'react';
import { connect } from 'react-redux';
import get from 'lodash/get';
import includes from 'lodash/includes';

import { recordViewedLocation } from './recentlyViewed';
import { ORGANIZATION_LEVEL_FLAG } from '../../util/constants';
import { convertFeatureFlagsObjectToListOfActiveFlags } from '../../util/util';

/*
 * Renders nothing. Whenever a production location finishes loading for
 * a signed-in member of an organization, it notes the location in that
 * user's recently viewed list (see recentlyViewed.js), which the
 * organization dashboard shows. Mounted once, next to the routes, so
 * neither production location page has to know about it.
 */
function RecentlyViewedRecorder({ userID, isMember, active, location }) {
    const osID = location ? location.os_id : null;

    useEffect(() => {
        if (active && isMember && userID && osID) {
            recordViewedLocation(userID, location);
        }
        // Keyed on the location's id: the same location re-rendering
        // with a new object must not count as another view.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [active, isMember, userID, osID]);

    return null;
}

function mapStateToProps({
    auth: {
        user: { user },
    },
    facilities: {
        singleFacility: { data },
    },
    featureFlags: { flags },
}) {
    const osID = get(data, 'id', null);

    return {
        userID: user && !user.isAnon ? user.id : null,
        isMember: Boolean(user && user.organization),
        active: includes(
            convertFeatureFlagsObjectToListOfActiveFlags(flags),
            ORGANIZATION_LEVEL_FLAG,
        ),
        location: osID
            ? {
                  os_id: osID,
                  name: get(data, 'properties.name', ''),
                  country_name: get(data, 'properties.country_name', ''),
              }
            : null,
    };
}

export default connect(mapStateToProps)(RecentlyViewedRecorder);
