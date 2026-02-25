export default theme =>
    Object.freeze({
        linkStyle: Object.freeze({
            display: 'inline-block',
            fontSize: '16px',
            background: 'none',
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            fontFamily: theme.typography.fontFamily,
        }),
        facilityName: Object.freeze({
            padding: '5px 0 15px',
        }),
        description: Object.freeze({
            fontWeight: 'bold',
            color: 'rgb(27, 27, 26)',
            fontSize: '16px',
        }),
        dialogActionsStyles: Object.freeze({
            display: 'flex',
            justifyContent: 'space-evenly',
            alignItems: 'center',
            padding: '10px',
        }),
        dialogContainerStyles: Object.freeze({
            padding: '10px',
        }),
        dialogTextFieldStyles: Object.freeze({
            width: '100%',
            marginTop: '10px',
            minWidth: '300px',
        }),
    });
