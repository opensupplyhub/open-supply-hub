import React, { useState, useEffect } from 'react';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import ConfirmNotFoundLocationDialog from './ConfirmNotFoundLocationDialog';
import ProductionLocationDetails from './ProductionLocationDetails';
import COLOURS from '../../util/COLOURS';

const makeSearchByNameAndAddressSuccessResultStyles = theme =>
    Object.freeze({
        searchResultsContainerStyles: Object.freeze({
            padding: '24px 5% 0 5%',
        }),
        titleStyles: Object.freeze({
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

const SearchByNameAndAddressSuccessResult = ({ data, classes }) => {
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
        console.log('I don’t see my Location');
    };

    const handleConfirmDialogClose = () => {
        setConfirmDialogIsOpen(false);
        console.log('Close');
    };

    const count = data?.data?.length || 0;

    return (
        <>
            <ConfirmNotFoundLocationDialog
                confirmDialogIsOpen={confirmDialogIsOpen}
                handleConfirmDialogClose={handleConfirmDialogClose}
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
                        {count} results
                    </Typography>
                    <Typography className={classes.resultsSortStyles}>
                        Sort By: <strong>Best match</strong>
                    </Typography>
                </div>
                <div>
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

export default withStyles(makeSearchByNameAndAddressSuccessResultStyles)(
    SearchByNameAndAddressSuccessResult,
);
