import { React, useState, useEffect } from 'react';
import { bool, func } from 'prop-types';
import { cloneDeep } from 'lodash';
import { connect } from 'react-redux';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import Select from 'react-select';
import CellElement from './CellElement';
import ConfirmActionButton from './ConfirmActionButton';
import FacilityListItemsDetailedTableRowCell from './FacilityListItemsDetailedTableRowCell';
import FacilityListItemsConfirmationTableRowItem from './FacilityListItemsConfirmationTableRowItem';
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
});

function FacilityListItemsConfirmationTableRow({
    item,
    makeConfirmMatchFunction,
    makeRejectMatchFunction,
    fetching,
    readOnly,
    className,
    openMergeModal,
    updateToMergeOSID,
    updateTargetOSID,
    fetchToMergeFacility,
}) {
    const {
        action,
        activeCheckboxes,
        activeSubmitButton,
        toggleCheckbox,
        handleSelectChange,
        isCheckboxDisabled,
    } = useCheckboxManager();

    const actionOptions = [
        { value: CONFIRM_ACTION, label: 'Action: Confirm' },
        { value: MERGE_ACTION, label: 'Action: Merge' },
        { value: REJECT_ACTION, label: 'Action: Reject' },
    ];

    const [matches, setMatches] = useState([]);
    useEffect(() => {
        setMatches(cloneDeep(item.matches));
    }, [item.matches]);

    useEffect(() => {
        if (action === MERGE_ACTION) {
            const uniqueOsIdItems = matches.reduce((acc, match) => {
                const currentConfidence = parseFloat(match.confidence);
                if (
                    !acc[match.os_id] ||
                    currentConfidence > parseFloat(acc[match.os_id].confidence)
                ) {
                    acc[match.os_id] = match;
                }
                return acc;
            }, {});

            const noDuplicateMatches = Object.values(uniqueOsIdItems);
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
                    colSpan={2}
                >
                    <CellElement item={item.name || ' '} />
                </TableCell>
                <TableCell
                    padding="default"
                    style={listTableCellStyles.addressCellStyles}
                    colSpan={2}
                >
                    <CellElement item={item.address || ' '} />
                </TableCell>
                <TableCell
                    padding="default"
                    style={listTableCellStyles.statusCellStyles}
                    colSpan={6}
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
                    colSpan={2}
                    style={listTableCellStyles.headerCellStyles}
                >
                    <b>Facility Match Name</b>
                </TableCell>
                <TableCell
                    padding="default"
                    variant="head"
                    style={listTableCellStyles.headerCellStyles}
                    colSpan={2}
                >
                    <b>Facility Match Address</b>
                </TableCell>
                <TableCell
                    colSpan={1}
                    style={{
                        padding: 0,
                    }}
                >
                    <Select
                        placeholder={actionOptions[0].label}
                        defaultValue={actionOptions[0].value}
                        onChange={option => handleSelectChange(option.value)}
                        options={actionOptions}
                        styles={selectStyles}
                        isSearchable={false}
                    />
                </TableCell>
                <TableCell
                    colSpan={2}
                    style={{
                        paddingTop: 0,
                        paddingLeft: '8px',
                    }}
                >
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
                        hasActions
                        action={action}
                        activeSubmitButton={activeSubmitButton}
                        activeCheckboxes={activeCheckboxes}
                        openMergeModal={openMergeModal}
                        updateTargetOSID={updateTargetOSID}
                        updateToMergeOSID={updateToMergeOSID}
                        fetchToMergeFacility={fetchToMergeFacility}
                        fetchTargetFacility={fetchToMergeFacility}
                    />
                </TableCell>
                <TableCell
                    padding="default"
                    variant="head"
                    colSpan={3}
                    style={{
                        ...listTableCellStyles.headerCellStyles,
                        textAlign: 'right',
                    }}
                >
                    <b>Confidence Score</b>
                </TableCell>
            </TableRow>
            {matches.map((
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
            ))}
        </>
    );
}

FacilityListItemsConfirmationTableRow.defaultProps = {
    readOnly: true,
};

FacilityListItemsConfirmationTableRow.propTypes = {
    item: facilityListItemPropType.isRequired,
    makeConfirmMatchFunction: func.isRequired,
    makeRejectMatchFunction: func.isRequired,
    fetching: bool.isRequired,
    readOnly: bool,
};

function mapStateToProps({
    facilityListDetails: {
        confirmOrRejectMatchOrRemoveItem: { fetching },
    },
}) {
    return {
        fetching,
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
