import React from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import ArrowRightAlt from '@material-ui/icons/ArrowRightAlt';

import { resetSingleFacility } from '../../../../actions/facilities';
import { facilitiesRoute } from '../../../../util/constants';

import productionLocationDetailsBackToSearchStyles from './styles';

function ProductionLocationDetailsBackToSearch({
    classes,
    clearFacility,
    history: { push },
}) {
    const onClick = event => {
        event.preventDefault();
        clearFacility();
        push(facilitiesRoute);
    };

    return (
        <div className={classes.buttonContainer}>
            <a
                href={facilitiesRoute}
                className={classes.backLink}
                onClick={onClick}
            >
                <ArrowRightAlt style={{ transform: 'rotate(180deg)' }} />
                <span className={classes.text}>Back to search results</span>
            </a>
        </div>
    );
}

function mapDispatchToProps(dispatch) {
    return {
        clearFacility: () => dispatch(resetSingleFacility()),
    };
}

export default connect(
    null,
    mapDispatchToProps,
)(
    withStyles(productionLocationDetailsBackToSearchStyles)(
        ProductionLocationDetailsBackToSearch,
    ),
);
