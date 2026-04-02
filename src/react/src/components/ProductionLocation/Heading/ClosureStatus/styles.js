import COLOURS from '../../../../util/COLOURS';

export default theme =>
    Object.freeze({
        status: {
            backgroundColor: COLOURS.BLACK,
            borderRadius: 0,
            display: 'flex',
            justifyContent: 'flex-start',
            marginBottom: theme.spacing.unit * 2,
        },
        contentContainer: {
            width: '100%',
            maxWidth: '1072px',
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            padding: theme.spacing.unit * 2,
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
            color: COLOURS.WHITE,
            fontSize: '24px',
            fontWeight: 'normal',
            position: 'relative',
            [theme.breakpoints.down(450)]: {
                display: 'none',
            },
        },
        iconSlash: {
            position: 'relative',
            display: 'inline-flex',
            '&::after': {
                content: '""',
                position: 'absolute',
                top: '10%',
                left: '50%',
                width: '2px',
                height: '80%',
                backgroundColor: COLOURS.WHITE,
                transform: 'translateX(-50%) rotate(-45deg)',
                transformOrigin: 'center',
            },
        },
        textBox: {
            display: 'flex',
            flexDirection: 'row',
            flexWrap: 'wrap',
            alignItems: 'center',
            textAlign: 'left',
        },
        text: {
            color: COLOURS.WHITE,
            fontSize: '1rem',
            textAlign: 'left',
        },
        statusPending: {
            marginLeft: theme.spacing.unit,
        },
    });
