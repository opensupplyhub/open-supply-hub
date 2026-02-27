import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import ArrowBack from '@material-ui/icons/ArrowBackIos';

import { resetSingleFacility } from '../../../actions/facilities';
import { facilitiesRoute } from '../../../util/constants';
import { shouldUseProductionLocationPage } from '../../../util/util';

import ProductionLocationDetailsContent from '../ProductionLocationDetailsContent/ProductionLocationDetailsContent';

import productionLocationDetailsStyles from './styles';

function ProductionLocationDetails({
    classes,
    clearFacility,
    history: { push },
    data,
    embed,
    useProductionLocationPage,
    location,
}) {
    return (
        <div className={classes.container}>
            <div className={classes.buttonContainer}>
                <Button
                    color="primary"
                    className={classes.backButton}
                    onClick={() => {
                        clearFacility();
                        push(facilitiesRoute);
                    }}
                >
                    <ArrowBack />
                    Back to search results
                </Button>
            </div>
            <p>Production Location Details</p>
            <ProductionLocationDetailsContent
                data={data}
                embed={embed}
                clearFacility={clearFacility}
                useProductionLocationPage={useProductionLocationPage}
                location={location}
            />
        </div>
    );
}

function mapStateToProps({
    filters,
    embeddedMap: { embed },
    facilities: { singleFacility: { data } = {} } = {},
    featureFlags,
}) {
    return {
        filters,
        embedded: !!embed,
        data,
        embed,
        useProductionLocationPage: shouldUseProductionLocationPage(featureFlags),
    };
}

function mapDispatchToProps(dispatch) {
    return {
        clearFacility: () => dispatch(resetSingleFacility()),
    };
}

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps,
    )(withStyles(productionLocationDetailsStyles)(ProductionLocationDetails)),
);
