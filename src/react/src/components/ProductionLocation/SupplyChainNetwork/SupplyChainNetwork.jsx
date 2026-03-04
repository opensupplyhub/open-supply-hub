import React, { useState, useMemo, useCallback } from 'react';
import { object, arrayOf, shape, string, number, bool } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';

import SupplyChainNetworkDrawer from './SupplyChainNetworkDrawer/SupplyChainNetworkDrawer';
import {
    splitContributorsIntoPublicAndNonPublic,
    makeProfileRouteLink,
} from '../../../util/util';
import supplyChainNetworkStyles from './styles';

const buildTypeCounts = contributors => {
    const totals = contributors.reduce((acc, contributor) => {
        const type = contributor.contributor_type;
        if (!type) return acc;
        const count = contributor.count || 1;
        acc[type] = (acc[type] || 0) + count;
        return acc;
    }, {});

    return Object.entries(totals).map(([type, count]) => ({ type, count }));
};

const getTotalCount = contributors =>
    contributors.reduce((sum, c) => sum + (c.count || 1), 0);

const SupplyChainNetwork = ({ classes, contributors }) => {
    const [isOpen, setIsOpen] = useState(false);
    const handleOpen = useCallback(() => setIsOpen(true), []);
    const handleClose = useCallback(() => setIsOpen(false), []);

    const visibleContributors = useMemo(
        () => contributors.filter(c => !!c.contributor_name || !!c.name),
        [contributors],
    );

    const { publicContributors, nonPublicContributors } = useMemo(
        () => splitContributorsIntoPublicAndNonPublic(visibleContributors),
        [visibleContributors],
    );

    const filteredNonPublic = useMemo(
        () => nonPublicContributors.filter(c => c.contributor_type != null),
        [nonPublicContributors],
    );

    const typeCounts = useMemo(() => buildTypeCounts(visibleContributors), [
        visibleContributors,
    ]);

    // totalCount is based on what is actually shown in the drawer to keep counts consistent
    const totalCount = useMemo(
        () => getTotalCount([...publicContributors, ...filteredNonPublic]),
        [publicContributors, filteredNonPublic],
    );

    if (!visibleContributors.length) return null;

    return (
        <div className={classes.container}>
            <Typography className={classes.title} component="h3">
                Supply Chain Network
            </Typography>
            <Typography className={classes.subtitle} component="p">
                Organizations that have shared information about this production
                location.
            </Typography>

            {typeCounts.length > 0 && (
                <div className={classes.typeCounts}>
                    {typeCounts.map(({ type, count }) => (
                        <Typography
                            key={type}
                            className={classes.typeCount}
                            component="p"
                        >
                            <span className={classes.typeCountNumber}>
                                {count}
                            </span>{' '}
                            {type}
                        </Typography>
                    ))}
                </div>
            )}

            {publicContributors.length > 0 && (
                <div className={classes.contributorList}>
                    {publicContributors.map(contributor => (
                        <Link
                            key={contributor.id}
                            to={makeProfileRouteLink(contributor.id)}
                            className={classes.contributorLink}
                        >
                            {contributor.contributor_name}
                        </Link>
                    ))}
                </div>
            )}

            <Button
                className={classes.triggerButton}
                onClick={handleOpen}
                disableRipple
            >
                View all {totalCount} data sources
            </Button>

            <SupplyChainNetworkDrawer
                open={isOpen}
                onClose={handleClose}
                totalCount={totalCount}
                typeCounts={typeCounts}
                publicContributors={publicContributors}
                nonPublicContributors={filteredNonPublic}
            />
        </div>
    );
};

SupplyChainNetwork.propTypes = {
    classes: object.isRequired,
    contributors: arrayOf(
        shape({
            id: number,
            contributor_name: string,
            name: string,
            contributor_type: string,
            list_name: string,
            count: number,
            is_verified: bool,
        }),
    ),
};

SupplyChainNetwork.defaultProps = {
    contributors: [],
};

export default withStyles(supplyChainNetworkStyles)(SupplyChainNetwork);
