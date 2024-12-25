import React, { useState, useEffect } from 'react';
import { connect } from 'react-redux';
import { func, object, bool, array } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';

import BackToSearchButton from './BackToSearchButton';
import { contributeProductionLocationRoute } from '../../util/constants';
import history from '../../util/history';
import { fetchProductionLocations } from '../../actions/contributeProductionLocation';
import ProductionLocationDetails from './ProductionLocationDetails';
import COLOURS from '../../util/COLOURS';

const makeSearchByNameAndAddressResultStyles = theme =>
    Object.freeze({
        circularProgressContainerStyles: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: 'calc(100vh - 116px)',
        }),
        mainContainerStyles: Object.freeze({
            padding: '48px 5% 0 5%',
        }),
        mainTitleStyles: Object.freeze({
            fontWeight: theme.typography.fontWeightExtraBold,
            fontSize: '56px',
            lineHeight: '60px',
            marginBottom: '16px',
        }),
        descriptionStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '21px',
            marginBottom: '32px',
            maxWidth: '656px',
        }),
        subTitleStyles: Object.freeze({
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            fontSize: '36px',
            lineHeight: '44px',
            margin: '32px 0 24px 0',
        }),
        resultsInfoContainerStyles: Object.freeze({
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px',
        }),
        resultsInfoStyles: Object.freeze({
            fontSize: '16px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightBold,
        }),
        resultsSortStyles: Object.freeze({
            fontSize: '16px',
            lineHeight: '20px',
        }),
        resultContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'space-between',
            gap: '10px',
            padding: '12px',
            borderBottom: `1px solid ${COLOURS.ACCENT_GREY}`,
            '&:hover': {
                backgroundColor: COLOURS.LIGHT_GREY,
            },
            '&:last-child': {
                marginBottom: '32px',
            },
        }),
        buttonBaseStyles: Object.freeze({
            height: '48px',
            borderRadius: 0,
            textTransform: 'none',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.common.black,
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
        selectButtonStyles: Object.freeze({
            minWidth: '100px',
        }),
        selectButtonLabelStyles: Object.freeze({
            fontSize: '16px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightExtraBold,
        }),
        notFoundButtonOuterContainerStyles: Object.freeze({
            position: 'sticky',
            bottom: -108,
            height: '188px',
        }),
        notFoundButtonContainerStyles: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            boxShadow: '0px -2px 12px 0px #00000014',
            position: 'sticky',
            bottom: 0,
            padding: '0 5%',
            height: '80px',
            backgroundColor: '#fff',
        }),
        notFoundButtonContainerScrolledStyles: Object.freeze({
            boxShadow: 'none',
        }),
        notFoundButtonStyles: Object.freeze({
            width: '275px',
        }),
        notFoundButtonLabelStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '22px',
            fontWeight: theme.typography.fontWeightExtraBold,
        }),
    });

const SearchByNameAndAddressResult = ({
    data,
    fetching,
    fetchLocations,
    classes,
}) => {
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

    console.log('data >>>', data);
    console.log('fetching >>>', fetching);
    useEffect(() => {
        fetchLocations();
    }, [fetchLocations]);

    const count = data?.data?.length || 0;

    const handleBackToSearchByNameAddress = () => {
        // clearProductionLocations();
        history.push(`${contributeProductionLocationRoute}?tab=name-address`);
    };

    const handleSelectLocation = () => {
        console.log('Select');
    };

    const handleNotFoundLocation = () => {
        console.log('I don’t see my Location');
    };

    if (fetching) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    return (
        <>
            <div className={classes.mainContainerStyles}>
                <BackToSearchButton
                    label="Back to ID search"
                    handleBackToSearch={handleBackToSearchByNameAddress}
                />
                <Typography component="h1" className={classes.mainTitleStyles}>
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
                        {count} results
                    </Typography>
                    <Typography className={classes.resultsSortStyles}>
                        Sort By: <strong>Best match</strong>
                    </Typography>
                </div>
                {data?.data &&
                    data?.data.map(location => (
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
                                color="secondary"
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
                        color="secondary"
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

SearchByNameAndAddressResult.defaultProps = {
    data: [],
    fetching: false,
};

SearchByNameAndAddressResult.propTypes = {
    data: array,
    fetching: bool,
    fetchLocations: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        productionLocations: { data, fetching },
    },
}) => ({
    data,
    fetching,
});
const mapDispatchToProps = dispatch => ({
    fetchLocations: () => dispatch(fetchProductionLocations()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(
    withStyles(makeSearchByNameAndAddressResultStyles)(
        SearchByNameAndAddressResult,
    ),
);
