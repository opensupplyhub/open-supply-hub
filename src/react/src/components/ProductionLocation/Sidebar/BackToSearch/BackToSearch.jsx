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
    history,
}) {
    const onClick = event => {
        event.preventDefault();
        clearFacility();

        if (history.length > 1) {
            history.goBack();
        } else {
            history.push(facilitiesRoute);
        }
    };

    return (
        <div className={classes.buttonContainer}>
            <button
                type="button"
                className={classes.backLink}
                onClick={onClick}
                data-testid="back-to-search-button"
            >
                <ArrowRightAlt
                    data-testid="back-to-search-arrow"
                    style={{ transform: 'rotate(180deg)' }}
                />
                <span
                    className={classes.text}
                    data-testid="back-to-search-text"
                >
                    Back to search results
                </span>
            </button>
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
