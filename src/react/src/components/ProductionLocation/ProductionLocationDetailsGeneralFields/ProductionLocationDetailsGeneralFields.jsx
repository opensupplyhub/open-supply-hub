import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import DataPoint, { STATUS_CLAIMED } from '../DataPoint/DataPoint';
import ContributionsDrawer from '../ContributionsDrawer/ContributionsDrawer';

import styles from './styles';

/**
 * Build mock drawer data for testing the data point + drawer integration.
 * Replace with real API data when available.
 */
function getMockDrawerDataForName(facilityName) {
    const base = facilityName || 'Production location';
    return {
        title: 'All Data Contributions',
        subtitle: (
            <>
                7 organizations have contributed data for{' '}
                <strong>{base}</strong>
            </>
        ),
        promotedContribution: {
            value: base,
            sourceName: 'Zaber and Zubair Fabrics Ltd',
            date: '2022-11-15',
            linkUrl: null,
        },
        contributions: [
            {
                value: 'Noman Group Bangladesh',
                sourceName: 'International Accord Foundation',
                date: '2025-12-01',
                linkUrl: null,
            },
            {
                value: 'Noman Group',
                sourceName: 'Marks & Spencer',
                date: '2025-08-01',
                linkUrl: null,
            },
            {
                value: 'The Noman Group',
                sourceName: 'JD Williams',
                date: '2025-05-01',
                linkUrl: null,
            },
        ],
    };
}

/**
 * Render extended fields, activity reports.
 * Show FacilityDetailsClaimedInfo in <FeatureFlag flag={CLAIM_A_FACILITY}>
 */
const ProductionLocationDetailsGeneralFields = ({ classes, data }) => {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const facilityName =
        data && data.properties && data.properties.name
            ? data.properties.name
            : null;

    const drawerData = facilityName
        ? getMockDrawerDataForName(facilityName)
        : null;

    const openDrawer = useCallback(() => setDrawerOpen(true), []);
    const closeDrawer = useCallback(() => setDrawerOpen(false), []);

    return (
        <div className={classes.container}>
            <Typography
                variant="title"
                className={classes.title}
                component="h3"
            >
                Location Identity
            </Typography>
            <DataPoint
                label="Production Location Name"
                value={facilityName || '—'}
                tooltipText="The name of the production facility as reported by contributors."
                statusLabel={STATUS_CLAIMED}
                contributorName={
                    facilityName ? 'Zaber and Zubair Fabrics Ltd' : null
                }
                date={facilityName ? '2022-11-15' : null}
                drawerData={drawerData}
                onOpenDrawer={openDrawer}
                renderDrawer={() => (
                    <ContributionsDrawer
                        open={drawerOpen}
                        onClose={closeDrawer}
                        title={drawerData?.title}
                        subtitle={drawerData?.subtitle}
                        promotedContribution={
                            drawerData?.promotedContribution || null
                        }
                        contributions={drawerData?.contributions || []}
                    />
                )}
            />
        </div>
    );
};

ProductionLocationDetailsGeneralFields.propTypes = {
    classes: PropTypes.object.isRequired,
    data: PropTypes.shape({
        properties: PropTypes.shape({
            name: PropTypes.string,
        }),
    }),
};

ProductionLocationDetailsGeneralFields.defaultProps = {
    data: null,
};

export default withStyles(styles)(ProductionLocationDetailsGeneralFields);
