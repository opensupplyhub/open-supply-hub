export default theme =>
    Object.freeze({
        status: {
            backgroundColor: 'rgb(40, 39, 39)',
            borderRadius: 0,
            display: 'flex',
            justifyContent: 'flex-start',
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            padding: theme.spacing.unit,
            paddingLeft: 0,
        },
        iconColumn: {
            flex: '0 0 36px',
            width: 36,
            minWidth: 36,
            maxWidth: 36,
            boxSizing: 'border-box',
            paddingRight: theme.spacing.unit * 1.5,
            paddingLeft: 0,
            paddingTop: 0,
            paddingBottom: 0,
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
        },
        icon: {
            fontSize: '24px',
            fontWeight: 'normal',
        },
        textBox: {
            display: 'flex',
            flexDirection: 'row',
            flexWrap: 'wrap',
            alignItems: 'center',
            textAlign: 'left',
        },
        text: {
            color: 'rgb(255, 255, 255)',
            fontSize: '14px',
            textAlign: 'left',
        },
        statusPending: {
            marginLeft: theme.spacing.unit,
        },
    });
