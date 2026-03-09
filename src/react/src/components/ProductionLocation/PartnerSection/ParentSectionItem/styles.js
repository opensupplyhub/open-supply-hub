export default theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            border: '1px solid #E7E8EA',
            borderRadius: '8px',
            marginBottom: theme.spacing.unit * 2,
            overflow: 'hidden',
        }),
        header: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 3}px`,
            cursor: 'pointer',
            '&:focus': {
                outline: 'none',
            },
        }),
        headerLeft: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${theme.spacing.unit}px`,
        }),
        headerRight: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${theme.spacing.unit / 2}px`,
        }),
        iconImage: Object.freeze({
            flexShrink: 0,
        }),
        title: Object.freeze({
            fontSize: '18px',
            fontWeight: 700,
            lineHeight: '22px',
        }),
        infoIcon: Object.freeze({
            fontSize: '20px',
            color: '#6E707E',
            cursor: 'pointer',
        }),
        toggleLabel: Object.freeze({
            fontSize: '14px',
            fontWeight: 500,
            color: '#6E707E',
        }),
        switchWrapper: Object.freeze({
            zIndex: 1,
        }),
        contentArea: Object.freeze({
            padding: `0 ${theme.spacing.unit * 3}px ${
                theme.spacing.unit * 3
            }px`,
        }),
        disclaimer: Object.freeze({
            backgroundColor: '#F9F7F7',
            borderRadius: '4px',
            padding: `${theme.spacing.unit * 2}px`,
            marginTop: theme.spacing.unit * 3,
        }),
        disclaimerText: Object.freeze({
            fontSize: '14px',
            lineHeight: '20px',
            color: '#191919',
            '& p': {
                margin: 0,
                display: 'inline',
            },
        }),
        disclaimerLabel: Object.freeze({
            fontWeight: 700,
            color: '#8428FA',
        }),
    });
