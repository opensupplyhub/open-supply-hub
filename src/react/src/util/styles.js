import { OARColor } from './constants';

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
    badgeCellStyles: Object.freeze({
        padding: '15px 0',
        textAlign: 'right',
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
            position: 'relative',
        }),
        input: Object.freeze({
            padding: '8px 56px 11px 16px',
            fontSize: '16px',
        }),
        inputFocused: Object.freeze({
            border: '1px solid #3d2f8c',
            boxShadow: '0px 0px 8px -1px rgba(12, 70, 225,0.5)',
        }),
        adornment: Object.freeze({
            maxHeight: '2.375em',
            position: 'absolute',
            top: 0,
            right: 0,
        }),
        adornmentPositionEnd: {
            margin: 0,
        },
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

export const makeSelectFilterStyles = (windowWidth, color = OARColor) =>
    Object.freeze({
        multiValue: Object.freeze(provided => ({
            ...provided,
            background: '#C0EBC7',
            borderRadius: '100px',
            fontFamily: 'Darker Grotesque',
            fontWeight: 700,
            fontSize: '14px',
            lineHeight: '16px',
            paddingLeft: '5px',
            paddingRight: '5px',
        })),
        control: Object.freeze((provided, state) => {
            const isInUse = state.isFocused || state.menuIsOpen;
            return {
                ...provided,
                borderRadius: 0,
                '*': {
                    boxShadow: 'none !important',
                },
                boxShadow: 'none',
                borderColor: isInUse ? color : provided.borderColor,
                '&:hover': {
                    borderColor: isInUse ? color : provided.borderColor,
                },
            };
        }),
        clearIndicator: Object.freeze(provided => ({
            ...provided,
            padding:
                windowWidth > 699 && windowWidth < 900 ? 0 : provided.padding,
        })),
    });

export const makeNestedSelectFilterStyles = Object.freeze({
    group: provided =>
        Object.freeze({
            ...provided,
            padding: '0',
        }),
    groupHeading: (provided, state) =>
        Object.freeze({
            ...provided,
            color: 'black',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            margin: '0',
            padding: '5px 12px',
            '&:hover': {
                backgroundColor: state.theme.colors.primary25,
            },
        }),
    option: (provided, state) =>
        Object.freeze({
            ...provided,
            padding: '1px 12px 1px 55px',
            backgroundColor: state.isFocused
                ? 'transparent'
                : provided.backgroundColor,
            '&:hover': {
                backgroundColor: state.theme.colors.primary25,
            },
        }),
});

export const makeCustomGroupHeadingStyles = Object.freeze({
    groupHeadingIconButton: Object.freeze({
        display: 'flex',
        padding: 0,
    }),
    groupHeadingButtonBase: Object.freeze({
        display: 'flex',
        justifyContent: 'flex-start',
        textAlign: 'left',
        width: '100%',
        fontWeight: 700,
        fontSize: '16px',
        cursor: 'default',
    }),
});

export const makeCustomDropdownIndicatorStyles = Object.freeze({
    dropdownIndicator: Object.freeze({
        display: 'flex',
        marginRight: '0.5em',
    }),
});
