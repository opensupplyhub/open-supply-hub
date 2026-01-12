const partnerFieldsSectionStyles = theme =>
    Object.freeze({
        root: {
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
            borderTop: '2px solid #F9F7F7',
            borderBottom: '2px solid #F9F7F7',
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            paddingTop: theme.spacing.unit * 3,
            paddingLeft: theme.spacing.unit * 3,
            paddingBottom: theme.spacing.unit * 3,
        },
        partnerFieldsTitle: {
            fontSize: '24px',
            fontWeight: 700,
        },
        partnerFieldsLink: {
            fontWeight: 500,
            fontSize: '18px',
            lineHeight: '21px',
        },
    });

export default partnerFieldsSectionStyles;
