import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '@material-ui/core/Button';

import {
    clearRecentlyViewedLocations,
    getRecentlyViewedLocations,
} from './recentlyViewed';
import { formatDate, makeFacilityDetailLink } from '../../util/util';
import { DATE_FORMATS } from '../../util/constants';
import styles from './styles';

/*
 * The production locations the signed-in member opened most recently.
 * The list is each person's own and is kept in their browser only, so
 * it is not shared with the organization and starts empty on another
 * device.
 */
const DashboardRecentlyViewed = ({ userID }) => {
    const [locations, setLocations] = useState(() =>
        getRecentlyViewedLocations(userID),
    );

    const clear = () => {
        clearRecentlyViewedLocations(userID);
        setLocations([]);
    };

    return (
        <div style={styles.section} data-testid="dashboard-recently-viewed">
            <h3 style={styles.sectionTitle}>Recently viewed</h3>
            <p style={styles.sectionHint}>
                Production locations you opened lately. Only you see this list,
                and it is kept in this browser only.
            </p>
            {locations.length === 0 ? (
                <p style={styles.meta}>
                    Production locations you open will appear here.
                </p>
            ) : (
                <>
                    <ul style={styles.plainList}>
                        {locations.map(location => (
                            <li
                                key={location.os_id}
                                style={styles.plainListItem}
                            >
                                <Link
                                    to={makeFacilityDetailLink(location.os_id)}
                                >
                                    {location.name || location.os_id}
                                </Link>
                                <span style={styles.meta}>
                                    {' '}
                                    {[location.country_name, location.os_id]
                                        .filter(Boolean)
                                        .join(' · ')}
                                    {', viewed '}
                                    {formatDate(
                                        location.viewed_at,
                                        DATE_FORMATS.LONG,
                                    )}
                                </span>
                            </li>
                        ))}
                    </ul>
                    <Button size="small" onClick={clear}>
                        Clear this list
                    </Button>
                </>
            )}
        </div>
    );
};

export default DashboardRecentlyViewed;
