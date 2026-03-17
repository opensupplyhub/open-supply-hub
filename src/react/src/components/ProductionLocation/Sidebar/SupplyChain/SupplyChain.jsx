import React from 'react';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';

import SupplyChainNetworkDrawer from './SupplyChainNetworkDrawer/SupplyChainNetworkDrawer';
import { makeProfileRouteLink } from '../../../../util/util';
import { pluralizeContributorType } from './utils';
import { useDrawerOpen, useDerivedContributors } from './hooks';
import supplyChainStyles from './styles';

const SupplyChain = ({ classes, contributors = [] }) => {
    const { isOpen, onOpen, onClose, triggerRef } = useDrawerOpen();
    const {
        visibleContributors,
        typeCounts,
        totalCount,
        sortedPublicContributors,
        aggregatedNonPublic,
    } = useDerivedContributors(contributors);

    if (!visibleContributors.length) return null;

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
                <Grid container className={classes.typeCounts}>
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
                </Grid>
            )}
            {sortedPublicContributors.length > 0 && (
                <Grid container className={classes.contributorList}>
                    {sortedPublicContributors.map(contributor => (
                        <Grid item key={contributor.id}>
                            <Link
                                to={makeProfileRouteLink(contributor.id)}
                                className={classes.contributorLink}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {contributor.contributor_name}
                            </Link>
                        </Grid>
                    ))}
                </Grid>
            )}
            {totalCount > 0 && (
                <Button
                    ref={triggerRef}
                    className={classes.triggerButton}
                    onClick={onOpen}
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
                onClose={onClose}
                totalCount={totalCount}
                typeCounts={typeCounts}
                publicContributors={sortedPublicContributors}
                nonPublicContributors={aggregatedNonPublic}
            />
        </div>
    );
};

const mapStateToProps = ({
    facilities: { singleFacility: { data } = {} } = {},
}) => ({
    contributors: data?.properties?.contributors ?? [],
});

export default connect(mapStateToProps)(
    withStyles(supplyChainStyles)(SupplyChain),
);
