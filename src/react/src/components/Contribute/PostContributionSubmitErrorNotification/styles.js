export const postContributionSubmitErrorNotificationStyles = () =>
    Object.freeze({
        mainText: Object.freeze({
            fontSize: '18px',
            fontWeight: '500',
        }),
        errorList: Object.freeze({
            padding: '0',
            listStyleType: 'disc',
        }),
    });

export const notificationContainerStyles = () =>
    Object.freeze({
        notificationWrapper: Object.freeze({
            flexWrap: 'nowrap',
            padding: '10px',
            backgroundColor: '#FFEAEA',
        }),
        icon: Object.freeze({
            color: '#191919',
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
        }),
    });

export const errorContentStyles = () =>
    Object.freeze({
        title: Object.freeze({
            fontSize: '18px',
            fontWeight: '700',
        }),
        mainText: Object.freeze({
            fontSize: '18px',
            fontWeight: '500',
        }),
        rawErrorDataContentWrapper: Object.freeze({
            borderRadius: '4px',
            boxSizing: 'border-box',
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
