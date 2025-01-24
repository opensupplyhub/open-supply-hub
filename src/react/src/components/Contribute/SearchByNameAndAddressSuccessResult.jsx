import React, { useEffect, useState, useCallback } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { connect } from 'react-redux';
import { arrayOf, func, object } from 'prop-types';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { makeSearchByNameAndAddressSuccessResultStyles } from '../../util/styles';
import { productionLocationPropType } from '../../util/propTypes';
import ConfirmNotFoundLocationDialog from './ConfirmNotFoundLocationDialog';
import ProductionLocationDetails from './ProductionLocationDetails';
import {
    saveSearchParameters,
    clearSearchParameters,
} from '../../actions/searchParameters';

const SearchByNameAndAddressSuccessResult = ({
    productionLocations,
    clearLocations,
    classes,
    handleSaveSearchParameters,
    handleClearSearchParameters,
}) => {
    const history = useHistory();
    const location = useLocation();

    const [confirmDialogIsOpen, setConfirmDialogIsOpen] = useState(false);
    const [isScrolledToBottom, setIsScrolledToBottom] = useState(false);

    useEffect(() => {
        handleClearSearchParameters();
    }, []);

    useEffect(() => {
        const handleScroll = () => {
            const isAtBottom =
                window.innerHeight + window.scrollY >=
                document.getElementById('mainPanel').offsetHeight;
            setIsScrolledToBottom(isAtBottom);
        };

        window.addEventListener('scroll', handleScroll);
        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    const handleSelectLocation = useCallback(
        productionLocation => {
            if (location?.search) {
                const queryParams = new URLSearchParams(location.search);
                const name = queryParams.get('name');
                const address = queryParams.get('address');
                const country = queryParams.get('country');
                handleSaveSearchParameters({ name, address, country });
            }
            const baseUrl = `/contribute/production-location/${productionLocation.os_id}/info/`;
            history.push(baseUrl);
        },
        [handleSaveSearchParameters, history, location],
    );

    const handleNotFoundLocation = () => {
        setConfirmDialogIsOpen(true);
    };

    const handleConfirmDialogClose = () => {
        setConfirmDialogIsOpen(false);
    };

    return (
        <>
            <ConfirmNotFoundLocationDialog
                confirmDialogIsOpen={confirmDialogIsOpen}
                handleConfirmDialogClose={handleConfirmDialogClose}
                clearLocations={clearLocations}
            />
            <div className={classes.searchResultsContainerStyles}>
                <Typography component="h1" className={classes.titleStyles}>
                    Search results
                </Typography>
                <Typography className={classes.descriptionStyles}>
                    We found results that closely match your search criteria.
                    Since names and addresses on OS Hub are user-provided, there
                    may be slight differences between what you entered and
                    what&apos;s shown below. Find the best match for the
                    production location you are looking for in the list below,
                    click “Select” to edit the name, address and country, and to
                    add more information.
                </Typography>
                <Typography component="h3" className={classes.subTitleStyles}>
                    Locations
                </Typography>
                <div className={classes.resultsInfoContainerStyles}>
                    <Typography className={classes.resultsInfoStyles}>
                        {productionLocations.length} results
                    </Typography>
                    <Typography className={classes.resultsSortStyles}>
                        Sort By: <strong>Best match</strong>
                    </Typography>
                </div>
                <div>
                    {productionLocations.map(productionLocation => (
                        <div
                            key={productionLocation.os_id}
                            className={classes.resultContainer}
                        >
                            <ProductionLocationDetails
                                osId={productionLocation.os_id}
                                name={productionLocation.name}
                                address={productionLocation.address}
                                countryName={productionLocation.country.name}
                            />
                            <Button
                                variant="contained"
                                onClick={() =>
                                    handleSelectLocation(productionLocation)
                                }
                                classes={{
                                    root: `${classes.buttonBaseStyles} ${classes.selectButtonStyles}`,
                                    label: classes.selectButtonLabelStyles,
                                }}
                            >
                                Select
                            </Button>
                        </div>
                    ))}
                </div>
            </div>

            <div className={classes.notFoundButtonOuterContainerStyles}>
                <div
                    className={`${classes.notFoundButtonContainerStyles} ${
                        isScrolledToBottom
                            ? classes.notFoundButtonContainerScrolledStyles
                            : ''
                    }`}
                >
                    <Button
                        variant="contained"
                        onClick={handleNotFoundLocation}
                        classes={{
                            root: `${classes.buttonBaseStyles} ${classes.notFoundButtonStyles}`,
                            label: classes.notFoundButtonLabelStyles,
                        }}
                    >
                        I don&apos;t see my Location
                    </Button>
                </div>
            </div>
        </>
    );
};

SearchByNameAndAddressSuccessResult.propTypes = {
    productionLocations: arrayOf(productionLocationPropType).isRequired,
    clearLocations: func.isRequired,
    classes: object.isRequired,
    handleSaveSearchParameters: func.isRequired,
    handleClearSearchParameters: func.isRequired,
};

function mapDispatchToProps(dispatch) {
    return {
        handleSaveSearchParameters: parameters =>
            dispatch(saveSearchParameters(parameters)),
        handleClearSearchParameters: () => dispatch(clearSearchParameters()),
    };
}

export default connect(
    null,
    mapDispatchToProps,
)(
    withStyles(makeSearchByNameAndAddressSuccessResultStyles)(
        SearchByNameAndAddressSuccessResult,
    ),
);
