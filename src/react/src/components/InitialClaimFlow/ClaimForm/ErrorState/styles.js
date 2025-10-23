const errorStateStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: '#F9F7F7',
            padding: '48px 0 120px 0',
        }),
        paper: Object.freeze({
            padding: '40px 40px',
            backgroundColor: '#FFFFFF',
            boxShadow: 'none',
            borderRadius: 0,
            marginTop: '32px',
        }),
        errorContainer: Object.freeze({
            padding: theme.spacing.unit * 3,
            textAlign: 'center',
        }),
        errorText: Object.freeze({
            color: theme.palette.error.main,
            marginBottom: theme.spacing.unit * 2,
        }),
        errorButton: Object.freeze({
            marginTop: theme.spacing.unit * 2,
        }),
    });

export default errorStateStyles;
