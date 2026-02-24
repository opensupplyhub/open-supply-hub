import React from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import ArrowBack from '@material-ui/icons/ArrowBackIos';

import { resetSingleFacility } from '../../../actions/facilities';
import { facilitiesRoute } from '../../../util/constants';

import ProductionLocationDetailsContent from '../ProductionLocationDetailsContent';

import styles from './styles';

function ProductionLocationDetails({ classes, clearFacility, history: { push } }) {
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
            <ProductionLocationDetailsContent />
        </div>
    );
}

function mapStateToProps({ filters, embeddedMap: { embed } }) {
    return { filters, embedded: !!embed };
}

function mapDispatchToProps(dispatch) {
    return {
        clearFacility: () => dispatch(resetSingleFacility()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(styles)(ProductionLocationDetails));
