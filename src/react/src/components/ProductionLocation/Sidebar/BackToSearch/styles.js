export default theme => ({
    buttonContainer: {
        marginBottom: theme.spacing.unit * 2,
    },
    backLink: {
        fontSize: `1.25rem`,
        textTransform: 'none',
        width: '100%',
        fontWeight: 700,
        display: 'flex',
        alignItems: 'center',
        textDecoration: 'none',
    },
    icon: {
        transform: 'rotate(180deg)',
        fontSize: `1.75rem`,
    },
    text: {
        fontSize: `1.25rem`,
        fontWeight: 700,
        display: 'inline-block',
        marginBottom: theme.spacing.unit / 2,
        marginLeft: theme.spacing.unit / 2,
    },
});
