import COLOURS from '../../../util/COLOURS';

export const postContributionSubmitErrorNotificationStyles = () =>
    Object.freeze({
        errorList: Object.freeze({
            padding: '0',
        }),
        bulletIcon: Object.freeze({
            fontSize: '6px',
            color: COLOURS.JET_BLACK,
        }),
    });

export const notificationContainerStyles = () =>
    Object.freeze({
        notificationWrapper: Object.freeze({
            flexWrap: 'nowrap',
            padding: '10px',
            backgroundColor: COLOURS.LIGHT_RED,
        }),
        icon: Object.freeze({
            color: COLOURS.JET_BLACK,
        }),
        closeButtonWrapper: Object.freeze({
            marginLeft: 'auto',
        }),
        closeButton: Object.freeze({
            padding: '0',
        }),
        errorContentWrapper: Object.freeze({
            padding: '0 10px',
            maxWidth: '800px',
            '& p, & h3, & ul': Object.freeze({
                // Redefine the styles for all the necessary elements to override the styles set by the MUI classes.
                fontSize: '18px',
            }),
        }),
    });

export const errorContentStyles = () =>
    Object.freeze({
        title: Object.freeze({
            fontWeight: '700',
        }),
        rawErrorDataContentWrapper: Object.freeze({
            borderRadius: '4px',
            boxSizing: 'border-box',
            padding: '10px 12px',
            '&::after': Object.freeze({
                content: 'none',
            }),
            '&::before': Object.freeze({
                content: 'none',
            }),
        }),
        rawErrorDataContainer: Object.freeze({
            margin: '10px 0 15px 0',
        }),
        buttonText: Object.freeze({
            padding: '0 8px',
            textTransform: 'none',
            fontSize: '16px',
        }),
    });
