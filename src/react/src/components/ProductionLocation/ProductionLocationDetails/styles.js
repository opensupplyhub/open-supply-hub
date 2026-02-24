export default theme => ({
    container: {
        backgroundColor: '#F9F7F7',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: 0,
        [theme.breakpoints.up('md')]: {
            paddingLeft: '4.5rem',
            paddingRight: '4.5rem',
        },
    },
    buttonContainer: {
        height: '4.5rem',
        display: 'flex',
        justifyContent: 'flex-start',
        alignItems: 'center',
    },
    backButton: {
        textTransform: 'none',
        fontWeight: 700,
    },
});
