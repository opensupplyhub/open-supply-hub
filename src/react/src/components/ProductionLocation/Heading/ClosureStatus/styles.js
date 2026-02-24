export default theme =>
    Object.freeze({
        status: {
            backgroundColor: 'rgb(40, 39, 39)',
            borderRadius: 0,
            display: 'flex',
            justifyContent: 'center',
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            padding: theme.spacing.unit,
        },
        icon: {
            fontSize: '24px',
            fontWeight: 'normal',
            paddingLeft: theme.spacing.unit * 2,
            paddingRight: theme.spacing.unit * 3,
        },
        textBox: {
            display: 'flex',
            flexDirection: 'column',
        },
        text: {
            color: 'rgb(255, 255, 255)',
            fontSize: '14px',
        },
    });
