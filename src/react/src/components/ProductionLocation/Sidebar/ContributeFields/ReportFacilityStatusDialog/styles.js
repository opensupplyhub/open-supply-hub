export default () =>
    Object.freeze({
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
        dialogPaper: Object.freeze({
            borderRadius: 0,
            maxWidth: '700px',
            width: '100%',
        }),
        dialogTextFieldStyles: Object.freeze({
            width: '100%',
            marginTop: '10px',
            minWidth: '300px',
            '& fieldset': Object.freeze({
                borderRadius: 0,
            }),
        }),
    });
