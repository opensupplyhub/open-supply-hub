import { OARColor } from './constants';
import COLOURS from './COLOURS';
import { multiValueBackgroundHandler } from './util';

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

export const makeSelectFilterStyles = (windowWidth, origin, color = OARColor) =>
    Object.freeze({
        multiValue: Object.freeze((provided, state) => {
            const backgroundColor = multiValueBackgroundHandler(
                state.data.value,
                origin,
            );
            return {
                ...provided,
                background: backgroundColor,
                borderRadius: '100px',
                fontFamily: 'Darker Grotesque',
                fontWeight: 700,
                fontSize: '14px',
                lineHeight: '16px',
                paddingLeft: '5px',
                paddingRight: '5px',
            };
        }),
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

export const makeContributeProductionLocationStyles = theme =>
    Object.freeze({
        mainContainerStyles: Object.freeze({
            background: theme.palette.background.grey,
            padding: '48px 5% 120px 5%',
        }),
        titleStyles: Object.freeze({
            fontWeight: theme.typography.fontWeightExtraBold,
            fontSize: '56px',
            lineHeight: '60px',
        }),
        tabsContainerStyles: Object.freeze({
            flexGrow: 1,
            marginTop: '48px',
        }),
        tabsIndicatorStyles: Object.freeze({
            backgroundColor: theme.palette.primary.main,
            height: '4px',
        }),
        tabRootStyles: Object.freeze({
            textTransform: 'initial',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            width: '100%',
            maxWidth: '300px',
            borderBottom: `1px solid ${COLOURS.NEAR_BLACK}`,
            paddingBottom: '16px',
            '&$tabSelectedStyles': {
                fontWeight: theme.typography.fontWeightExtraBold,
            },
        }),
        tabLabelContainerStyles: Object.freeze({
            padding: '0 24px',
        }),
        tabSelectedStyles: Object.freeze({}),
    });

export const makeSearchByOsIdTabStyles = theme =>
    Object.freeze({
        helperTextContainerStyles: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
        }),
        infoIconStyles: Object.freeze({
            fontSize: '16px',
            verticalAlign: 'middle',
        }),
        helperTextStyles: Object.freeze({
            fontSize: '16px',
            fontWeight: theme.typography.fontWeightSemiBold,
            color: COLOURS.DARK_GREY,
        }),
        instructionTextStyles: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            margin: '24px 0 32px 0',
        }),
        searchContainerStyles: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            padding: '40px 110px',
            borderRadius: '0',
            boxShadow: 'none',
        }),
        mainTitleStyles: Object.freeze({
            fontSize: '36px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
        }),
        subTitleStyles: Object.freeze({
            fontSize: '21px',
            fontWeight: theme.typography.fontWeightSemiBold,
            margin: '8px 0 24px 0',
        }),
        textFieldStyles: Object.freeze({
            maxWidth: '528px',
        }),
        searchInputStyles: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            lineHeight: '22px',
            padding: '16px',
        }),
        notchedOutlineStyles: Object.freeze({
            borderRadius: 0,
        }),
        buttonLabel: Object.freeze({
            fontSize: '18px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightExtraBold,
        }),
        buttonStyles: Object.freeze({
            width: '200px',
            borderRadius: '0',
            textTransform: 'none',
            backgroundColor: theme.palette.action.main,
            marginTop: '26px',
            color: theme.palette.common.black,
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
    });

export const makeSearchByOsIdResultStyles = theme =>
    Object.freeze({
        circularProgressContainerStyles: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: 'calc(100vh - 116px)',
        }),
        mainContainerStyles: Object.freeze({
            backgroundColor: theme.palette.background.grey,
            padding: '48px 5% 120px 5%',
        }),
        mainTitleStyles: Object.freeze({
            fontWeight: theme.typography.fontWeightExtraBold,
            fontSize: '56px',
            lineHeight: '60px',
            margin: '40px 0 48px 0',
        }),
        resultContainerStyles: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            padding: '40px 110px',
            borderRadius: '0',
            boxShadow: 'none',
        }),
        resultTitleStyles: Object.freeze({
            fontSize: '36px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            lineHeight: '44px',
        }),
        resultSubTitleStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '21px',
            fontWeight: theme.typography.fontWeightSemiBold,
            margin: '8px 0 24px 0',
        }),
        locationDetailsStyles: Object.freeze({
            margin: '24px 0',
        }),
        locationNameStyles: Object.freeze({
            fontSize: '36px',
            lineHeight: '44px',
            fontWeight: theme.typography.fontWeightBold,
        }),
        locationCurrentOsIdStyles: Object.freeze({
            fontSize: '16px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightBold,
            marginTop: '8px',
        }),
        locationHistoricalOsIdStyles: Object.freeze({
            fontSize: '14px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightBold,
            color: COLOURS.DARK_GREY,
            marginTop: '8px',
        }),
        locationAddressContainerStyles: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            marginTop: '12px',
        }),
        locationAddressStyles: Object.freeze({
            fontSize: '16px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
    });

export const makeBackToSearchButtonStyles = theme =>
    Object.freeze({
        backButtonRootStyles: Object.freeze({
            textTransform: 'none',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
        }),
        backButtonLabelStyles: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
        }),
    });

const arrowGenerator = color => ({
    '&[x-placement*="bottom"] $arrowStyles': {
        top: 0,
        left: 0,
        marginTop: '-0.95em',
        width: '3em',
        height: '1em',
        '&::before': {
            borderWidth: '0 1em 1em 1em',
            borderColor: `transparent transparent ${color} transparent`,
        },
    },
    '&[x-placement*="top"] $arrowStyles': {
        bottom: 0,
        left: 0,
        marginBottom: '-0.95em',
        width: '3em',
        height: '1em',
        '&::before': {
            borderWidth: '1em 1em 0 1em',
            borderColor: `${color} transparent transparent transparent`,
        },
    },
    '&[x-placement*="right"] $arrowStyles': {
        left: 0,
        marginLeft: '-0.95em',
        height: '3em',
        width: '1em',
        '&::before': {
            borderWidth: '1em 1em 1em 0',
            borderColor: `transparent ${color} transparent transparent`,
        },
    },
    '&[x-placement*="left"] $arrowStyles': {
        right: 0,
        marginRight: '-0.95em',
        height: '3em',
        width: '1em',
        '&::before': {
            borderWidth: '1em 0 1em 1em',
            borderColor: `transparent transparent transparent ${color}`,
        },
    },
});

export const makePreviousOsIdTooltipStyles = theme =>
    Object.freeze({
        arrowPopperStyles: arrowGenerator(COLOURS.DARK_SLATE_GRAY),
        arrowStyles: Object.freeze({
            position: 'absolute',
            fontSize: 6,
            width: '22px',
            height: '12px',
            '&::before': {
                content: '""',
                margin: 'auto',
                display: 'block',
                width: 0,
                height: 0,
                borderStyle: 'solid',
            },
        }),
        tooltipStyles: Object.freeze({
            backgroundColor: COLOURS.DARK_SLATE_GRAY,
            color: COLOURS.WHITE,
            maxWidth: '149px',
            boxShadow: '0px 4px 4px 0px #00000040',
        }),
        placementLeftStyles: Object.freeze({
            margin: '0 8px',
        }),
        placementRightStyles: Object.freeze({
            margin: '0 8px',
        }),
        placementTopStyles: Object.freeze({
            margin: '8px 0',
        }),
        placementBottomStyles: Object.freeze({
            margin: '8px 0',
        }),
        tooltipTitleStyles: Object.freeze({
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightMedium,
        }),
        infoOutlinedIconStyles: Object.freeze({
            fontSize: '16px',
            verticalAlign: 'middle',
        }),
    });

export const makeSearchByOsIdResultActionsStyles = theme =>
    Object.freeze({
        actionsStyles: Object.freeze({
            display: 'flex',
            gap: '24px',
        }),
        buttonLabelStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightExtraBold,
            letterSpacing: '-0.05px',
        }),
        buttonBaseStyles: Object.freeze({
            width: '265px',
            height: '49px',
            borderRadius: '0',
            textTransform: 'none',
        }),
        defaultButtonStyles: Object.freeze({
            color: theme.palette.common.black,
            borderColor: COLOURS.NEAR_BLACK,
        }),
        secondaryButtonStyles: Object.freeze({
            backgroundColor: theme.palette.action.main,
            color: theme.palette.common.black,
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
    });

export const makeDatePickerStyles = theme => ({
    datePickerContainer: {
        display: 'flex',
        alignItems: 'center',
        gap: '5px',
    },
    datePickerLabel: {
        fontSize: '18px',
        fontWeight: theme.typography.fontWeightSemiBoldPlus,
    },
    dateInputStyles: Object.freeze({
        fontSize: '16px',
        lineHeight: '20px',
        padding: '8px',
    }),
    notchedOutlineStyles: Object.freeze({
        borderRadius: 0,
    }),
});

export const makeDownloadExcelButtonStyles = theme =>
    Object.freeze({
        button: Object.freeze({
            width: '200px',
            marginBottom: '44px',
            padding: '14px 13px',
            color: theme.palette.common.black,
            fontSize: '18px',
            fontWeight: 900,
            lineHeight: '20px',
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
            backgroundColor: theme.palette.action.main,
        }),
        buttonContent: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            textTransform: 'none',
        }),
        buttonText: Object.freeze({
            marginLeft: '0.2rem',
        }),
    });

export const makeDashboardModerationQueueStyles = theme =>
    Object.freeze({
        mainContainer: Object.freeze({
            marginBottom: '60px',
            width: '100%',
        }),
        dashboardFilters: Object.freeze({
            padding: '20px',
        }),
        datePickersContainer: Object.freeze({
            width: '100%',
            marginTop: '5px',
        }),
        errorText: Object.freeze({
            marginTop: '5px',
        }),
        numberResults: Object.freeze({
            fontWeight: theme.typography.fontWeightBold,
            padding: '20px',
        }),
    });

export const makeDashboardModerationQueueListTableStyles = Object.freeze({
    tableContainerStyles: Object.freeze({
        overflowX: 'auto',
    }),
    rowStyles: Object.freeze({
        cursor: 'pointer',
    }),
    emptyRowStyles: Object.freeze({
        height: '5px',
    }),
    loaderStyles: Object.freeze({
        display: 'block',
        margin: 'auto',
    }),
    pendingStatusStyles: Object.freeze({
        backgroundColor: COLOURS.PALE_LIGHT_YELLOW,
    }),
    approvedStatusStyles: Object.freeze({
        backgroundColor: COLOURS.MINT_GREEN,
    }),
    rejectedStatusStyles: Object.freeze({
        backgroundColor: COLOURS.LIGHT_RED,
    }),
});

export const makeDashboardModerationQueueTableHeaderStyles = theme =>
    Object.freeze({
        headerCellStyles: Object.freeze({
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
        }),
    });
