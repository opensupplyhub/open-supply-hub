import { React, useState, useEffect } from 'react';
import { bool, func, string } from 'prop-types';
import { cloneDeep } from 'lodash';
import { connect } from 'react-redux';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import Select from 'react-select';
import ShowOnly from './ShowOnly';
import CellElement from './CellElement';
import ConfirmActionButton from './ConfirmActionButton';
import FacilityListItemsDetailedTableRowCell from './FacilityListItemsDetailedTableRowCell';
import FacilityListItemsConfirmationTableRowItem from './FacilityListItemsConfirmationTableRowItem';
import FacilityListItemsConfirmationTableRowNoMerge from './FacilityListItemsConfirmationTableRowNoMerge';
import { useCheckboxManager } from '../util/hooks';

import { toggleMergeModal } from '../actions/ui';

import {
    confirmFacilityListItemMatch,
    rejectFacilityListItemMatch,
} from '../actions/facilityListDetails';

import {
    updateMergeTargetFacilityOSID,
    fetchMergeTargetFacility,
    updateFacilityToMergeOSID,
    fetchFacilityToMerge,
} from '../actions/mergeFacilities';

import { facilityListItemPropType } from '../util/propTypes';

import { listTableCellStyles } from '../util/styles';

import {
    uploadedFileRowIndexOffset,
    CONFIRM_ACTION,
    MERGE_ACTION,
    REJECT_ACTION,
} from '../util/constants';

const selectStyles = Object.freeze({
    input: provided =>
        Object.freeze({
            ...provided,
            padding: '10px',
        }),
    menu: provided =>
        Object.freeze({
            ...provided,
            zIndex: '2',
        }),
    control: provided =>
        Object.freeze({
            ...provided,
            width: '140px',
        }),
});

function FacilityListItemsConfirmationTableRow({
    item,
    makeConfirmMatchFunction,
    makeRejectMatchFunction,
    fetching,
    readOnly,
    className,
    openMergeModal,
    targetFacilityOSID,
    facilityToMergeOSID,
    updateToMergeOSID,
    updateTargetOSID,
    fetchToMergeFacility,
    fetchTargetFacility,
}) {
    const {
        action,
        activeCheckboxes,
        activeSubmitButton,
        toggleCheckbox,
        resetCheckboxes,
        handleSelectChange,
        isCheckboxDisabled,
    } = useCheckboxManager();

    const actionOptions = [
        { value: CONFIRM_ACTION, label: 'Action: Confirm' },
        { value: MERGE_ACTION, label: 'Action: Merge' },
        { value: REJECT_ACTION, label: 'Action: Reject' },
    ];

    const [matches, setMatches] = useState([]);

    const filterUniqueMatches = matchList => {
        const uniqueOsIdItems = matchList.reduce((acc, matchItem) => {
            const currentConfidence = parseFloat(matchItem.confidence);
            if (
                !acc[matchItem.os_id] ||
                currentConfidence > parseFloat(acc[matchItem.os_id].confidence)
            ) {
                acc[matchItem.os_id] = matchItem;
            }
            return acc;
        }, {});

        return Object.values(uniqueOsIdItems);
    };

    useEffect(() => {
        setMatches(cloneDeep(item.matches));
        if (action === MERGE_ACTION) {
            const noDuplicateMatches = filterUniqueMatches(item.matches);
            setMatches(noDuplicateMatches.length > 1 ? noDuplicateMatches : []);
            handleSelectChange(actionOptions[1].value);
        }
    }, [item.matches]);

    useEffect(() => {
        if (action === MERGE_ACTION) {
            const noDuplicateMatches = filterUniqueMatches(matches);
            setMatches(noDuplicateMatches.length > 1 ? noDuplicateMatches : []);
        } else {
            setMatches(cloneDeep(item.matches));
        }
    }, [action]);

    return (
        <>
            <TableRow
                hover={false}
                style={{
                    background: '#dcfbff',
                    verticalAlign: 'top',
                    borderTop: '1px solid #e0e0e0',
                }}
                className={className}
            >
                <TableCell
                    align="center"
                    padding="default"
                    style={listTableCellStyles.rowIndexStyles}
                >
                    <CellElement
                        item={item.row_index + uploadedFileRowIndexOffset}
                    />
                </TableCell>
                <TableCell
                    align="center"
                    padding="default"
                    style={listTableCellStyles.countryNameStyles}
                >
                    <CellElement item={item.country_name || ' '} />
                </TableCell>
                <TableCell
                    padding="default"
                    style={listTableCellStyles.nameCellStyles}
                    colSpan={1}
                >
                    <CellElement item={item.name || ' '} />
                </TableCell>
                <TableCell
                    padding="default"
                    style={listTableCellStyles.addressCellStyles}
                    colSpan={3}
                >
                    <CellElement item={item.address || ' '} />
                </TableCell>
                <TableCell
                    padding="default"
                    style={listTableCellStyles.statusCellStyles}
                >
                    <FacilityListItemsDetailedTableRowCell
                        title={item.status}
                        stringIsHidden
                        hasActions={false}
                        fetching={fetching}
                        readOnly={readOnly}
                        data={[]}
                    />
                </TableCell>
            </TableRow>
            <TableRow
                hover={false}
                style={{
                    background: '#dcfbff',
                    verticalAlign: 'top',
                    border: 0,
                }}
                className={className}
            >
                <TableCell padding="default" variant="head" colSpan={2} />
                <TableCell
                    padding="default"
                    variant="head"
                    style={listTableCellStyles.headerCellStyles}
                >
                    <b>Facility Match Name</b>
                </TableCell>
                <TableCell
                    padding="default"
                    variant="head"
                    style={listTableCellStyles.headerCellStyles}
                >
                    <b>Facility Match Address</b>
                </TableCell>
                <TableCell
                    colSpan={2}
                    style={{
                        padding: 0,
                    }}
                >
                    <ShowOnly when={!readOnly}>
                        <div
                            style={{
                                display: 'flex',
                                paddingLeft: '25px',
                            }}
                        >
                            <Select
                                placeholder={actionOptions[0].label}
                                defaultValue={actionOptions[0].value}
                                onChange={option =>
                                    handleSelectChange(option.value)
                                }
                                options={actionOptions}
                                styles={selectStyles}
                                isSearchable={false}
                                menuPortalTarget={document.body}
                            />
                            <ConfirmActionButton
                                listItem={item}
                                confirmMatch={makeConfirmMatchFunction(
                                    activeCheckboxes[0]?.id,
                                )}
                                rejectMatch={makeRejectMatchFunction(
                                    activeCheckboxes.map(
                                        facilityMatchToReject =>
                                            facilityMatchToReject?.id,
                                    ),
                                )}
                                buttonName="OK"
                                fetching={fetching}
                                action={action}
                                resetCheckboxes={resetCheckboxes}
                                activeSubmitButton={activeSubmitButton}
                                activeCheckboxes={activeCheckboxes}
                                openMergeModal={openMergeModal}
                                targetFacilityOSID={targetFacilityOSID}
                                facilityToMergeOSID={facilityToMergeOSID}
                                updateTargetOSID={updateTargetOSID}
                                updateToMergeOSID={updateToMergeOSID}
                                fetchToMergeFacility={fetchToMergeFacility}
                                fetchTargetFacility={fetchTargetFacility}
                            />
                        </div>
                    </ShowOnly>
                </TableCell>
                <TableCell
                    padding="default"
                    variant="head"
                    style={{
                        ...listTableCellStyles.headerCellStyles,
                        textAlign: 'left',
                    }}
                >
                    <b>Confidence Score</b>
                </TableCell>
            </TableRow>
            {matches.length === 0 && action === MERGE_ACTION ? (
                <FacilityListItemsConfirmationTableRowNoMerge
                    className={className}
                />
            ) : (
                matches.map((
                    { id, status, address, os_id, name, confidence }, // eslint-disable-line camelcase
                ) => (
                    <FacilityListItemsConfirmationTableRowItem
                        key={id}
                        id={id}
                        os_id={os_id} // eslint-disable-line camelcase
                        name={name}
                        status={status}
                        className={className}
                        activeCheckboxes={activeCheckboxes}
                        address={address}
                        isCheckboxDisabled={isCheckboxDisabled}
                        confidence={confidence}
                        readOnly={readOnly}
                        toggleCheckbox={toggleCheckbox}
                        action={action}
                    />
                ))
            )}
        </>
    );
}

FacilityListItemsConfirmationTableRow.defaultProps = {
    readOnly: true,
    targetFacilityOSID: '',
    facilityToMergeOSID: '',
};

FacilityListItemsConfirmationTableRow.propTypes = {
    item: facilityListItemPropType.isRequired,
    makeConfirmMatchFunction: func.isRequired,
    makeRejectMatchFunction: func.isRequired,
    fetching: bool.isRequired,
    readOnly: bool,
    targetFacilityOSID: string,
    facilityToMergeOSID: string,
};

function mapStateToProps({
    facilityListDetails: {
        confirmOrRejectMatchOrRemoveItem: { fetching },
    },
    mergeFacilities: {
        targetFacility: { osID: targetFacilityOSID },
        facilityToMerge: { osID: facilityToMergeOSID },
    },
}) {
    return {
        fetching,
        targetFacilityOSID,
        facilityToMergeOSID,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        makeConfirmMatchFunction: matchID => () =>
            dispatch(confirmFacilityListItemMatch(matchID)),
        makeRejectMatchFunction: matchIDs => () =>
            dispatch(rejectFacilityListItemMatch(matchIDs)),
        openMergeModal: () => dispatch(toggleMergeModal()),
        updateTargetOSID: osID => dispatch(updateMergeTargetFacilityOSID(osID)),
        updateToMergeOSID: osID => dispatch(updateFacilityToMergeOSID(osID)),
        fetchToMergeFacility: () => dispatch(fetchFacilityToMerge()),
        fetchTargetFacility: () => dispatch(fetchMergeTargetFacility()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(FacilityListItemsConfirmationTableRow);
