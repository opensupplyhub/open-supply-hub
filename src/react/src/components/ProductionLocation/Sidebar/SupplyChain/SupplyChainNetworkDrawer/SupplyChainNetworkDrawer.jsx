import React from 'react';
import { object, bool, func, arrayOf, shape, string, number } from 'prop-types';
import Drawer from '@material-ui/core/Drawer';
import Divider from '@material-ui/core/Divider';
import { withStyles } from '@material-ui/core/styles';

import supplyChainNetworkDrawerStyles from './styles';
import DrawerHeader from './DrawerHeader/DrawerHeader';
import DrawerSubtitle from './DrawerSubtitle/DrawerSubtitle';
import InfoBoxSection from './InfoBoxSection/InfoBoxSection';
import TypeSummarySection from './TypeSummarySection/TypeSummarySection';
import PublicContributorsSection from './PublicContributorsSection/PublicContributorsSection';
import AnonymizedSection from './AnonymizedSection/AnonymizedSection';

const SupplyChainNetworkDrawer = ({
    classes,
    open,
    onClose,
    totalCount,
    typeCounts,
    publicContributors,
    nonPublicContributors,
}) => (
    <Drawer anchor="right" open={open} onClose={onClose}>
        <div
            className={classes.drawerContent}
            data-testid="supply-chain-drawer"
        >
            <DrawerHeader onClose={onClose} />
            <DrawerSubtitle totalCount={totalCount} />
            <Divider className={classes.divider} />
            <InfoBoxSection />
            {typeCounts.length > 0 && (
                <TypeSummarySection typeCounts={typeCounts} />
            )}
            {publicContributors.length > 0 && (
                <>
                    <Divider className={classes.divider} />
                    <PublicContributorsSection
                        publicContributors={publicContributors}
                    />
                </>
            )}
            {nonPublicContributors.length > 0 && (
                <>
                    <Divider className={classes.divider} />
                    <AnonymizedSection
                        nonPublicContributors={nonPublicContributors}
                    />
                </>
            )}
        </div>
    </Drawer>
);

SupplyChainNetworkDrawer.propTypes = {
    classes: object.isRequired,
    open: bool.isRequired,
    onClose: func.isRequired,
    totalCount: number,
    typeCounts: arrayOf(
        shape({
            type: string.isRequired,
            count: number.isRequired,
        }),
    ),
    publicContributors: arrayOf(
        shape({
            id: number.isRequired,
            contributor_name: string.isRequired,
            contributor_type: string,
            list_names: arrayOf(string),
        }),
    ),
    nonPublicContributors: arrayOf(
        shape({
            contributor_type: string.isRequired,
            count: number.isRequired,
        }),
    ),
};

SupplyChainNetworkDrawer.defaultProps = {
    totalCount: 0,
    typeCounts: [],
    publicContributors: [],
    nonPublicContributors: [],
};

export default withStyles(supplyChainNetworkDrawerStyles)(
    SupplyChainNetworkDrawer,
);
