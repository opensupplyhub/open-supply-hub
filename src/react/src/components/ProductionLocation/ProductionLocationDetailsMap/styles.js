export default theme =>
    Object.freeze({
        root: {
            color: '#191919',
            display: 'flex',
            justifyContent: 'center',
            borderTop: '2px solid #F9F7F7',
            borderBottom: '2px solid #F9F7F7',
        },
        contentContainer: {
            width: '320px',
            height: '200px',
            padding: theme.spacing.unit * 3,
            [theme.breakpoints.up('sm')]: {
                width: '385px',
                maxWidth: '100%',
            },
            [theme.breakpoints.up('md')]: {
                width: '100%',
                maxWidth: '1072px',
                height: '457px',
                maxHeight: '100%',
            },
        },
        title: {
            marginBottom: theme.spacing.unit,
        },
        dragHint: {
            fontSize: '0.875rem',
            color: theme.palette.text.secondary,
            marginBottom: theme.spacing.unit,
        },
    });
