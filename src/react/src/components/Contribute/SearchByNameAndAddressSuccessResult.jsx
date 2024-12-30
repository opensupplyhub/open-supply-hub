import React, { useEffect, useState } from 'react';
import { arrayOf, func, number, object } from 'prop-types';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { makeSearchByNameAndAddressSuccessResultStyles } from '../../util/styles';
import { productionLocationPropType } from '../../util/propTypes';
import ConfirmNotFoundLocationDialog from './ConfirmNotFoundLocationDialog';
import ProductionLocationDetails from './ProductionLocationDetails';

const SearchByNameAndAddressSuccessResult = ({
    productionLocationsCount,
    productionLocations,
    clearLocations,
    classes,
}) => {
    const [confirmDialogIsOpen, setConfirmDialogIsOpen] = useState(false);
    const [isScrolledToBottom, setIsScrolledToBottom] = useState(false);

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

    const handleSelectLocation = () => {
        console.log('Select');
    };

    const handleNotFoundLocation = () => {
        setConfirmDialogIsOpen(true);
        console.log('I do not see my Location');
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
                        {productionLocationsCount} results
                    </Typography>
                    <Typography className={classes.resultsSortStyles}>
                        Sort By: <strong>Best match</strong>
                    </Typography>
                </div>
                <div>
                    {productionLocations.map(location => (
                        <div
                            key={location.os_id}
                            className={classes.resultContainer}
                        >
                            <ProductionLocationDetails
                                osId={location.os_id}
                                name={location.name}
                                address={location.address}
                                countryName={location.country.name}
                            />
                            <Button
                                variant="contained"
                                onClick={handleSelectLocation}
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
    productionLocationsCount: number.isRequired,
    productionLocations: arrayOf(productionLocationPropType).isRequired,
    clearLocations: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeSearchByNameAndAddressSuccessResultStyles)(
    SearchByNameAndAddressSuccessResult,
);
