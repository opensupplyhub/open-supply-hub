export const formValidationErrorMessageStyle = Object.freeze({
    color: 'red',
    fontSize: '16px',
    fontWeight: '500',
    paddingLeft: '1.5rem',
    paddingBottom: '1rem',
});

export const listTableCellStyles = Object.freeze({
    rowIndexStyles: Object.freeze({
        fontSize: '16px',
        padding: '10px 24px',
    }),
    countryNameStyles: Object.freeze({
        fontSize: '16px',
        padding: '10px 24px',
    }),
    nameCellStyles: Object.freeze({
        fontSize: '16px',
        padding: '10px 24px',
    }),
    errorTextStyles: Object.freeze({
        color: 'red',
        whiteSpace: 'pre-wrap',
    }),
    addressCellStyles: Object.freeze({
        fontSize: '16px',
        padding: '10px 24px',
        wordBreak: 'break-word',
    }),
    statusCellStyles: Object.freeze({
        fontSize: '16px',
        padding: '10px 24px',
        width: '300px',
    }),
    compareCellStyles: Object.freeze({
        fontSize: '16px',
        padding: '10px 24px',
        borderColor: '#f3f3f3',
    }),
    headerCellStyles: Object.freeze({
        fontSize: '16px',
        padding: '10px 24px',
        color: 'black',
    }),
    noMergeCellStyles: Object.freeze({
        fontSize: '16px',
        padding: '10px 24px',
        borderColor: '#f3f3f3',
    }),
});

export const confirmRejectMatchRowStyles = Object.freeze({
    cellStyles: Object.freeze({
        marginTop: '3px',
        marginBottom: '3px',
        display: 'flex',
        flexDirection: 'column',
    }),
    cellOverflowStyles: Object.freeze({
        textOverflow: 'ellipsis',
        overflow: 'hidden',
    }),
    cellRowStyles: Object.freeze({
        minHeight: '55px',
        display: 'flex',
        alignItems: 'top',
        maxWidth: '400px',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'hidden',
    }),
    cellSubtitleStyles: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        maxWidth: '400px',
    }),
    errorCellRowStyles: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        color: 'red',
    }),
    cellHiddenHRStyles: Object.freeze({
        color: '#fff',
        borderTop: 'transparent',
    }),
    cellHRStyles: Object.freeze({}),
    cellActionStyles: Object.freeze({
        display: 'flex',
        width: '200px',
        marginRight: '10px',
        alignItems: 'center',
        justifyContent: 'space-between',
    }),
});

export const filterSidebarStyles = Object.freeze({
    controlPanelContentStyles: Object.freeze({
        height: 'inherit',
        overflow: 'auto',
    }),
});

export const makeFilterStyles = theme =>
    Object.freeze({
        inputLabelStyle: Object.freeze({
            fontFamily: theme.typography.fontFamily,
            fontSize: '18px',
            fontWeight: 700,
            color: '#000',
            padding: '0.5rem 0',
            display: 'flex',
            alignContent: 'center',
        }),
        selectStyle: Object.freeze({
            fontFamily: theme.typography.fontFamily,
        }),
        searchInput: Object.freeze({
            backgroundColor: '#fff',
            paddingLeft: 0,
            borderRadius: 0,
            paddingRight: 0,
        }),
        notchedOutline: Object.freeze({
            borderRadius: 0,
        }),
        searchAdornment: Object.freeze({
            padding: 0,
        }),
    });

export const togglePasswordFieldStyles = () =>
    Object.freeze({
        label: Object.freeze({
            marginBottom: '8px',
            opacity: 1,
            color: '#000000',
            fontSize: '14px',
            fontWeight: 900,
            letterSpacing: '0.5px',
            lineHeight: '14px',
            textTransform: 'uppercase',
        }),
        wrapper: Object.freeze({
            marginTop: '8px',
            boxSizing: 'border-box',
            border: '1px solid #D6D8DD',
        }),
        input: Object.freeze({
            padding: '6px 0 10px 16px',
        }),
        inputType: Object.freeze({
            height: '100%',
        }),
        inputFocused: Object.freeze({
            border: '1px solid #3d2f8c',
            boxShadow: '0px 0px 8px -1px rgba(12, 70, 225,0.5)',
        }),
        adornment: Object.freeze({
            maxHeight: '2.375em',
        }),
        button: Object.freeze({
            padding: '8px',
        }),
    });

export const claimAFacilityFormStyles = Object.freeze({
    textFieldStyles: Object.freeze({
        width: '95%',
        padding: '10px 0 10px',
    }),
    inputGroupStyles: Object.freeze({
        width: '100%',
        padding: '5px 0 5px',
    }),
    asideStyles: Object.freeze({
        padding: '5px 20px 5px 0',
    }),
});

export const claimAFacilitySupportDocsFormStyles = Object.freeze({
    textFieldStyles: Object.freeze({
        width: '50%',
        padding: '10px 0 10px',
    }),
    inputGroupStyles: Object.freeze({
        width: '100%',
        paddingTop: '50px',
    }),
    asideStyles: Object.freeze({
        padding: '5px 20px 5px 0',
    }),
});
