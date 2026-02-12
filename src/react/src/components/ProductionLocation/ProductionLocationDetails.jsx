import React from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import ArrowBack from '@material-ui/icons/ArrowBackIos';

import { resetSingleFacility } from '../../actions/facilities';
import { facilitiesRoute } from '../../util/constants';

import ProductionLocationDetailsContent from './ProductionLocationDetailsContent';

const productionLocationDetailsStyles = theme => ({
    container: {
        backgroundColor: '#F9F7F7',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: 0,
        [theme.breakpoints.up('md')]: {
            paddingLeft: '4.5rem',
            paddingRight: '4.5rem',
        },
    },
    buttonContainer: {
        height: '4.5rem',
        display: 'flex',
        justifyContent: 'flex-start',
        alignItems: 'center',
    },
    backButton: {
        textTransform: 'none',
        fontWeight: 700,
    },
});

function ProductionLocationDetails({
    classes,
    clearFacility,
    history: { push },
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
)(withStyles(productionLocationDetailsStyles)(ProductionLocationDetails));
