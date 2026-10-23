export default theme =>
    Object.freeze({
        dialogTitle: Object.freeze({
            paddingBottom: '4px',
        }),
        title: Object.freeze({
            fontSize: '24px',
        }),
        facilityName: Object.freeze({
            color: theme.palette.primary.main,
            fontSize: '16px',
            fontWeight: theme.typography.fontWeightMedium,
            padding: '8px 0 15px',
        }),
        description: Object.freeze({
            color: 'rgb(27, 27, 26)',
            fontSize: '16px',
            marginBottom: '5px',
        }),
        textField: Object.freeze({
            marginTop: '10px',
            minWidth: '300px',
            '& fieldset': Object.freeze({
                borderRadius: 0,
            }),
        }),
        error: Object.freeze({
            marginTop: '10px',
        }),
        dialogActions: Object.freeze({
            display: 'flex',
            justifyContent: 'space-evenly',
            alignItems: 'center',
            padding: '10px',
        }),
        dialogPaper: Object.freeze({
            borderRadius: 0,
            maxWidth: '700px',
            width: '100%',
        }),
    });
