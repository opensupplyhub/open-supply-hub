import React, { useState, useRef, useEffect } from 'react';
import { arrayOf, shape, string, number } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';

import SupplyChainNetworkDrawer from './SupplyChainNetworkDrawer/SupplyChainNetworkDrawer';
import {
    splitContributorsIntoPublicAndNonPublic,
    makeProfileRouteLink,
} from '../../../../util/util';
import pluralizeContributorType from './utils';
import supplyChainStyles from './styles';

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

// Aggregate non-public contributors by type so each type appears only once.
// This prevents duplicate React keys and duplicate rows in the drawer.
const aggregateByType = nonPublicContributors =>
    nonPublicContributors
        .filter(c => c.contributor_type != null)
        .reduce((acc, c) => {
            const existing = acc.find(
                x => x.contributor_type === c.contributor_type,
            );
            if (existing) {
                return acc.map(item =>
                    item.contributor_type === c.contributor_type
                        ? { ...item, count: item.count + (c.count || 1) }
                        : item,
                );
            }
            return [
                ...acc,
                { contributor_type: c.contributor_type, count: c.count || 1 },
            ];
        }, []);

const getTotalCount = contributors =>
    contributors.reduce((sum, c) => sum + (c.count || 1), 0);

const SupplyChain = ({ classes, contributors }) => {
    const [isOpen, setIsOpen] = useState(false);
    const triggerRef = useRef(null);
    const hasBeenOpenRef = useRef(false);

    useEffect(() => {
        if (isOpen) {
            hasBeenOpenRef.current = true;
        } else if (
            hasBeenOpenRef.current &&
            triggerRef.current &&
            typeof triggerRef.current.focus === 'function'
        ) {
            triggerRef.current.focus();
        }
    }, [isOpen]);

    const visibleContributors = contributors.filter(
        c => !!c.contributor_name || !!c.contributor_type,
    );

    if (!visibleContributors.length) return null;

    const {
        publicContributors,
        nonPublicContributors,
    } = splitContributorsIntoPublicAndNonPublic(visibleContributors);

    const sortedPublicContributors = [...publicContributors].sort((a, b) =>
        (a.contributor_type || '').localeCompare(b.contributor_type || ''),
    );
    const aggregatedNonPublic = aggregateByType(nonPublicContributors);
    const typeCounts = buildTypeCounts([
        ...sortedPublicContributors,
        ...aggregatedNonPublic,
    ]);
    const totalCount = getTotalCount([
        ...sortedPublicContributors,
        ...aggregatedNonPublic,
    ]);

    return (
        <div className={classes.container} data-testid="supply-chain-section">
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
                            <strong>{count}</strong>{' '}
                            {pluralizeContributorType(type, count)}
                        </Typography>
                    ))}
                </div>
            )}

            {sortedPublicContributors.length > 0 && (
                <div className={classes.contributorList}>
                    {sortedPublicContributors.map(contributor => (
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

            {totalCount > 0 && (
                <Button
                    ref={triggerRef}
                    className={classes.triggerButton}
                    onClick={() => setIsOpen(true)}
                    aria-haspopup="dialog"
                    aria-expanded={isOpen}
                    disableRipple
                    data-testid="supply-chain-view-all-button"
                >
                    View all {totalCount}{' '}
                    {totalCount === 1 ? 'data source' : 'data sources'}
                </Button>
            )}

            <SupplyChainNetworkDrawer
                open={isOpen}
                onClose={() => setIsOpen(false)}
                totalCount={totalCount}
                typeCounts={typeCounts}
                publicContributors={sortedPublicContributors}
                nonPublicContributors={aggregatedNonPublic}
            />
        </div>
    );
};

SupplyChain.propTypes = {
    contributors: arrayOf(
        shape({
            id: number,
            contributor_name: string,
            contributor_type: string,
            list_name: string,
            count: number,
        }),
    ),
};

SupplyChain.defaultProps = {
    contributors: [],
};

export default withStyles(supplyChainStyles)(SupplyChain);
